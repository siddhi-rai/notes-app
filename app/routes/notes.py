from typing import Optional
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models import User, Note, Tag, note_shares, note_tags
from app.schemas import NoteCreate, NoteUpdate, NoteResponse, NoteShareRequest, MessageResponse
from app.auth import get_current_user

router = APIRouter()


def note_to_response(note: Note) -> dict:
    return {
        "id": note.id,
        "title": note.title,
        "content": note.content,
        "created_at": note.created_at,
        "updated_at": note.updated_at,
        "tags": [tag.name for tag in note.tags] if note.tags else [],
    }


@router.get("/notes", response_model=list[NoteResponse], status_code=status.HTTP_200_OK)
def get_all_notes(
    page: Optional[int] = Query(None, ge=1, description="Page number (1-indexed)"),
    per_page: Optional[int] = Query(None, ge=1, le=100, description="Items per page"),
    tags: Optional[str] = Query(None, description="Comma-separated tag names to filter by"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Get notes owned by user OR shared with user
    query = db.query(Note).filter(
        or_(
            Note.owner_id == current_user.id,
            Note.shared_with.any(User.id == current_user.id),
        )
    )

    # Filter by tags if provided
    if tags:
        tag_names = [t.strip().lower() for t in tags.split(",") if t.strip()]
        if tag_names:
            query = query.filter(Note.tags.any(Tag.name.in_(tag_names)))

    query = query.order_by(Note.updated_at.desc())

    # Pagination
    if page is not None and per_page is not None:
        offset = (page - 1) * per_page
        query = query.offset(offset).limit(per_page)

    notes = query.all()
    return [note_to_response(note) for note in notes]


@router.get("/notes/{note_id}", response_model=NoteResponse, status_code=status.HTTP_200_OK)
def get_note_by_id(
    note_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    note = db.query(Note).filter(Note.id == note_id).first()

    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    # Check access: owner or shared with
    if note.owner_id != current_user.id and current_user not in note.shared_with:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have access to this note")

    return note_to_response(note)


@router.post("/notes", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def create_note(
    payload: NoteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    note = Note(
        title=payload.title,
        content=payload.content,
        owner_id=current_user.id,
    )

    # Handle tags
    if payload.tags:
        for tag_name in payload.tags:
            tag_name_lower = tag_name.strip().lower()
            if not tag_name_lower:
                continue
            tag = db.query(Tag).filter(Tag.name == tag_name_lower).first()
            if not tag:
                tag = Tag(name=tag_name_lower)
                db.add(tag)
            note.tags.append(tag)

    db.add(note)
    db.commit()
    db.refresh(note)

    return note_to_response(note)


@router.put("/notes/{note_id}", response_model=NoteResponse, status_code=status.HTTP_200_OK)
def update_note(
    note_id: str,
    payload: NoteUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    note = db.query(Note).filter(Note.id == note_id).first()

    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    if note.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only update your own notes")

    if payload.title is not None:
        note.title = payload.title
    if payload.content is not None:
        note.content = payload.content

    # Handle tags update
    if payload.tags is not None:
        note.tags.clear()
        for tag_name in payload.tags:
            tag_name_lower = tag_name.strip().lower()
            if not tag_name_lower:
                continue
            tag = db.query(Tag).filter(Tag.name == tag_name_lower).first()
            if not tag:
                tag = Tag(name=tag_name_lower)
                db.add(tag)
            note.tags.append(tag)

    note.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(note)

    return note_to_response(note)


@router.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    note = db.query(Note).filter(Note.id == note_id).first()

    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    if note.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own notes")

    db.delete(note)
    db.commit()
    return None


@router.post("/notes/{note_id}/share", response_model=MessageResponse, status_code=status.HTTP_200_OK)
def share_note(
    note_id: str,
    payload: NoteShareRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    note = db.query(Note).filter(Note.id == note_id).first()

    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    if note.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only share your own notes")

    # Find the user to share with
    share_user = db.query(User).filter(User.email == payload.share_with_email).first()
    if not share_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if share_user.id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot share a note with yourself")

    # Check if already shared
    if share_user in note.shared_with:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Note already shared with this user")

    note.shared_with.append(share_user)
    db.commit()

    return {"message": f"Note shared successfully with {payload.share_with_email}"}


# --- Stretch Goal: Full-text search ---
@router.get("/search", response_model=list[NoteResponse], status_code=status.HTTP_200_OK)
def search_notes(
    q: str = Query(..., min_length=1, description="Search keyword"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    keyword = f"%{q}%"
    notes = (
        db.query(Note)
        .filter(
            or_(
                Note.owner_id == current_user.id,
                Note.shared_with.any(User.id == current_user.id),
            )
        )
        .filter(
            or_(
                Note.title.ilike(keyword),
                Note.content.ilike(keyword),
            )
        )
        .order_by(Note.updated_at.desc())
        .all()
    )
    return [note_to_response(note) for note in notes]
