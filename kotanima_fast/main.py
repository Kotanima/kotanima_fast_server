import os

from dotenv import find_dotenv, load_dotenv
from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles

from database import (
    async_get_posts_for_review,
    async_set_dislike_status,
    async_set_selected_status,
)

load_dotenv(find_dotenv(raise_error_if_not_found=True))

app = FastAPI()
app.mount(
    "/static",
    StaticFiles(directory=os.getenv("STATIC_FOLDER_PATH")),
    name="static",
)

# hypercorn --keyfile key.pem --certfile cert.pem --bind "0.0.0.0:8000" -w 3 kotanima_fast/main:app --reload
# hypercorn --keyfile kaa.key --certfile kaa.crt --bind "0.0.0.0:8000" -w 3 kotanima_fast/main:app --reload
# openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 999 -nodes

# sudo nano /etc/systemd/system/hypercorn.service
# sudo systemctl restart hypercorn.socket


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
