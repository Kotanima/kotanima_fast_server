import os

import psycopg
from dotenv import find_dotenv, load_dotenv
from psycopg.rows import dict_row

load_dotenv(find_dotenv(raise_error_if_not_found=True))


def get_connection_string() -> str:
    return f"""dbname={os.environ.get("DB_NAME")} 
    user={os.environ.get("DB_USER_NAME")} 
    password={os.environ.get("DB_USER_PASSWORD")} 
    port=5432 host=localhost 
    """


async def async_get_posts_for_review(limit: int = 20) -> list:
    async with await psycopg.AsyncConnection.connect(get_connection_string()) as aconn:
        async with aconn.cursor(row_factory=dict_row) as acur:
            await acur.execute(
                """select mar.sub_name, mar.post_id, mar.is_checked, mar.phash
                from my_app_redditpost mar 
                left join my_app_vkpost mav on mar.phash=mav.phash 
                WHERE mav.phash is null
                AND (mar.phash NOT IN (SELECT DISTINCT phash FROM my_app_redditpost where       is_disliked=true))
                AND (mar.sub_name IN ('awwnime','fantasymoe','patchuu','awenime','moescape'))
                AND mar.is_downloaded=false
                AND mar.is_checked=false
                AND mar.is_disliked=false
                AND mar.is_selected=false
                LIMIT (%s)""",
                (limit,),
            )
            await acur.fetchone()
            res = []
            async for record in acur:
                res.append(record)

            return res


async def async_set_dislike_status(phash: str, dislike: str, checked: str) -> None:
    async with await psycopg.AsyncConnection.connect(get_connection_string()) as aconn:
        async with aconn.cursor(row_factory=dict_row) as acur:
            await acur.execute(
                """update my_app_redditpost set (is_disliked , is_checked, is_selected) = 
                ((%s), (%s), false) where phash=(%s)""",
                (dislike, checked, phash),
            )


async def async_set_selected_status(phash: str, status: str) -> None:
    async with await psycopg.AsyncConnection.connect(get_connection_string()) as aconn:
        async with aconn.cursor(row_factory=dict_row) as acur:
            await acur.execute(
                """UPDATE my_app_redditpost SET is_selected=(%s) WHERE phash=(%s) """,
                (status, phash),
            )
