import sqlite3
import datetime

BASE = 'db.sqlite3'


def SQL_register_new_user(tg_id, name, phone):
    conn = sqlite3.connect(BASE)
    cur = conn.cursor()
    time_create = datetime.datetime.now()
    exec_text = f"""
        INSERT INTO 'service_client' (name, phonenumber, user_id, time_create)
        VALUES ('{name}','{phone}','{tg_id}','{time_create}')
        """
    cur.execute(exec_text)
    conn.commit()
    conn.close()


def SQL_get_user_data(tg_id) -> dict:

    conn = sqlite3.connect(BASE)
    cur = conn.cursor()
    exec_text = f"SELECT * FROM 'service_client' WHERE user_id is '{tg_id}'"
    cur.execute(exec_text)
    result = cur.fetchone()
    conn.close()

    if isinstance(result, type(None)):
        return False

    formated_result = {
        'id': result[0],
        'name': result[1],
        'phone': result[2],
        'tg_id': result[4],
        }
    return formated_result


def SQL_put_user_phone(tg_id, phone):
    conn = sqlite3.connect(BASE)
    cur = conn.cursor()
    exec_text = f"UPDATE 'service_client' SET phonenumber={phone} WHERE user_id={tg_id}"
    cur.execute(exec_text)
    conn.commit()
    conn.close()
