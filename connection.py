import pymysql
import os
from dotenv import load_dotenv


load_dotenv()

db = pymysql.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    port=int(os.getenv("DB_PORT")),
    db=os.getenv("DB_NAME"),
    charset=os.getenv("DB_CHARSET")
)


def get_conditions():
    sql = ("SELECT upk.user_id, upk.id, p.product_url, p.product_name, p.store_name, k.keyword "
           "FROM user_product_keyword AS upk "
           "JOIN product_keyword pk ON upk.product_keyword_id = pk.id "
           "JOIN product p ON pk.product_id = p.id "
           "JOIN keyword k ON pk.keyword_id = k.id "
           "LEFT JOIN record r ON r.user_product_keyword_id = upk.id AND r.search_date = CURDATE() "
           "WHERE r.user_product_keyword_id IS NULL "
           "ORDER BY upk.user_id ASC;")

    cursor = db.cursor()
    cursor.execute(sql)
    p_list = cursor.fetchall()

    product_dict = {}
    for item in p_list:
        if item[0] not in product_dict:
            product_dict[item[0]] = []
        data = {
            "user_id": item[0],
            "upk_id": item[1],
            "p_url": item[2],
            "p_name": item[3],
            "s_name": item[4],
            "keyword": item[5],
            "ranking": -1,
            "result": [],
        }
        product_dict[item[0]].append(data)
    return product_dict


# ===========================================================================================


def insert_product_ranking(products_ranking, today):
    sql_insert_data: str = \
        "INSERT INTO rankflow.record (user_product_keyword_id, search_date, ranking) VALUES (%s, %s, %s)"
    cursor = db.cursor()

    for product in products_ranking:
        cursor.execute(sql_insert_data, (product.get("upk_id"), today, product.get("ranking")))
        db.commit()
