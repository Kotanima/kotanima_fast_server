from fastapi import FastAPI, Query

from database import (
    async_get_posts_for_review,
    async_set_dislike_status,
    async_set_selected_status,
)


app = FastAPI()

# hypercorn --keyfile key.pem --certfile cert.pem kotanima_fast/main:app --reload

# openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 999 -nodes


@app.get("/reddit_posts/")
async def get_posts(limit: int = 20):
    data = await async_get_posts_for_review(limit)
    if data is None:
        raise HTTPException(status_code=404, detail="Posts not found")
    return data


# updates posts selection status
@app.patch("/select/")
async def update_select_status(phash: str, status: bool):
    await async_set_selected_status(phash=phash, status=status)


# updates posts dislike status
@app.patch("/dislike/")
async def update_dislike_status(phash: str, dislike: bool, checked: bool):
    await async_set_dislike_status(phash=phash, dislike=dislike, checked=checked)
