from fastapi import APIRouter

router = APIRouter()


@router.get("/about")
def about():
    return {
        "name": "Siddhi Rai",
        "email": "siddhirai@example.com",
        "my features": {
            "Note Tagging": "Added the ability to tag/label notes with custom tags and filter notes by tags. This feature enhances note organization and retrieval, similar to how labels work in Gmail or tags in Notion. I chose this because categorization is essential for any note-taking app as the number of notes grows.",
            "Full-text Search": "Implemented a search endpoint (GET /search?q=keyword) that performs case-insensitive search across note titles and content. This makes it easy to find notes without remembering exact titles.",
            "Pagination": "Added optional pagination support on the GET /notes endpoint with page and per_page query parameters, enabling efficient loading of large note collections.",
        },
    }
