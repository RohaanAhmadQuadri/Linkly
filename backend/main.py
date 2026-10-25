from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
from database import get_db_connection
import secrets
import string

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class URLData(BaseModel):
    original_url: HttpUrl


def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits
    return "".join(secrets.choice(characters) for _ in range(length))


@app.get("/db-test")
def test_database():
    connection = get_db_connection()
    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id, original_url, short_code FROM urls")
        return {"data": cursor.fetchall()}

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


@app.post("/shorten")
def shorten_url(data: URLData):
    connection = get_db_connection()
    cursor = None

    try:
        cursor = connection.cursor()
        original_url = str(data.original_url)

        for _ in range(5):
            short_code = generate_short_code()

            cursor.execute(
                "SELECT id FROM urls WHERE short_code = %s",
                (short_code,)
            )

            if cursor.fetchone() is None:
                break
        else:
            raise HTTPException(
                status_code=500,
                detail="Could not generate a unique short code"
            )

        query = """
            INSERT INTO urls (original_url, short_code)
            VALUES (%s, %s)
        """
        cursor.execute(query, (original_url, short_code))
        connection.commit()

        return {
            "message": "URL shortened successfully",
            "original_url": original_url,
            "short_code": short_code,
            "short_url": f"http://127.0.0.1:8000/{short_code}"
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


@app.get("/{short_code}")
def redirect_url(short_code: str):
    connection = get_db_connection()
    cursor = None

    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT original_url FROM urls WHERE short_code = %s",
            (short_code,)
        )

        result = cursor.fetchone()

        if result is None:
            raise HTTPException(
                status_code=404,
                detail="Short URL not found"
            )

        return RedirectResponse(url=result[0], status_code=302)

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()
