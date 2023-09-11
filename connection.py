from dotenv import load_dotenv
import pymysql
import os

load_dotenv()

db = pymysql.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    port=int(os.getenv("DB_PORT")),
    db=os.getenv("DB_NAME"),
    charset=os.getenv("DB_CHARSET")
)
