from datetime import datetime, time, timedelta, date
import sqlite3
from tkinter import StringVar

BASE = 'db.sqlite3'


def sql_register_new_user(tg_id, name, phone):
    conn = sqlite3.connect(BASE)
    cur = conn.cursor()
    time_create = datetime.now()
    exec_text = f"""
        INSERT INTO 'service_client' (name, phonenumber, user_id, time_create)
        VALUES ('{name}','{phone}','{tg_id}','{time_create}')
        """
    cur.execute(exec_text)
    conn.commit()
    conn.close()


def sql_get_user_data(tg_id) -> dict:
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


def sql_put_user_phone(tg_id, phone):
    conn = sqlite3.connect(BASE)
    cur = conn.cursor()
    exec_text = f"UPDATE 'service_client' SET phonenumber={phone} WHERE user_id={tg_id}"
    cur.execute(exec_text)
    conn.commit()
    conn.close()


def registration_new_appointment(meet_date, meet_time, tg_id, master_id, service_id):
    connection = sqlite3.connect(BASE)
    cursor = connection.cursor()
    time_create = datetime.now()
    appointment_information = (meet_date, meet_time, tg_id, master_id, service_id)
    cursor.execute(
        "INSERT INTO service_appointment (appointment_date, appointment_time, client_id, master_id, service_id, time_create) VALUES (?, ?, ?, ?, ?, ?)",
        appointment_information + (time_create,))
    connection.commit()
    connection.close()




def get_masters_name_from_base():
    connection = sqlite3.connect(BASE)
    cursor = connection.cursor()
    all_masters = cursor.execute("SELECT name FROM service_master")
    masters = cursor.fetchall()
    masters_details = []
    for master in masters:
        masters_id = master[0]
        masters_details.append(masters_id)
    connection.close()
    return masters_details


def get_services_from_base():
    conn = sqlite3.connect(BASE)
    cur = conn.cursor()
    cur.execute("SELECT title FROM service_service")
    procedures = cur.fetchall()
    buttons = []
    for procedure in procedures:
        procedure_name = procedure[0]
        buttons.append(procedure_name)
    cur.close()
    conn.close()
    return buttons


def get_available_slots():
    conn = sqlite3.connect(BASE)
    cur = conn.cursor()
    today = datetime.now().date()
    cur.execute("SELECT appointment_time FROM service_appointment WHERE appointment_date >= ?", (today,))
    slots = cur.fetchall()
    conn.close()
    return [slot[0] for slot in slots]


def get_available_times(date):
    conn = sqlite3.connect(BASE)
    cur = conn.cursor()
    date_obj = datetime.strptime(date, '%d.%m').date()
    cur.execute("SELECT appointment_time FROM service_appointment WHERE date = ?", (date_obj,))
    available_times = cur.fetchall()
    conn.close()
    available_times = [time[0] for time in available_times]
    return available_times
