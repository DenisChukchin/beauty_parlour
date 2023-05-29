from datetime import datetime
import datetime
import sqlite3

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


def registration_new_appointment(meet_date, meet_time, tg_id, master_id=False, service_id=False):
    connection = sqlite3.connect(BASE)
    cursor = connection.cursor()
    time_create = datetime.datetime.now()

    appointment_information = [meet_date, meet_time, time_create, tg_id]
    if master_id:
        appointment_information.append(master_id)
        add_id = 'master_id'
    else:
        appointment_information.append(service_id)
        add_id = 'service_id'

    cursor.execute(
        f'''
        INSERT INTO service_appointment
        (appointment_date, appointment_time, time_create, client_id, {add_id})
        VALUES (?,?,?,?,?)
        ''',
        appointment_information
        )

    connection.commit()
    connection.close()


def get_masters_name_from_base():
    connection = sqlite3.connect(BASE)
    cursor = connection.cursor()
    all_masters = cursor.execute("SELECT * FROM service_master")
    masters = cursor.fetchall()
    connection.close()
    masters_details = {}
    for master in masters:
        masters_id = master[0]
        masters_details[masters_id] = \
            {all_masters.description[i][0]: master[i] for i in range(len(master))}
    return masters_details


def get_services_from_base():
    connection = sqlite3.connect(BASE)
    cursor = connection.cursor()
    all_services = cursor.execute("SELECT * FROM service_service")
    services = cursor.fetchall()
    connection.close()
    masters_details = {}
    for service in services:
        services_id = service[0]
        masters_details[services_id] = \
            {all_services.description[i][0]: service[i] for i in range(len(service))}
    return masters_details


def restoring_user_date_for_sql_query(client_date):
    cut_day = client_date[0:2]
    cut_month = client_date[3:5]
    year = datetime.date.today().year
    real_date_for_sql = f'{year}-{cut_month}-{cut_day}'
    return real_date_for_sql


def get_free_time(client_date, master_id=False, procedure_id=False):
    appointment_date = restoring_user_date_for_sql_query(client_date)
    all_appointment_time = [
        '10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:00',
        '13:30', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30',
        '17:00', '17:30', '18:00', '18:30', '19:00', '19:30', '20:00',
        '20:30'
    ]
    sql_filter = f"master_id={master_id}" if master_id else f"service_id={procedure_id}"
    connection = sqlite3.connect(BASE)
    cursor = connection.cursor()
    cursor.execute(f"SELECT appointment_time FROM service_appointment "
                   f"WHERE {sql_filter} "
                   f"AND appointment_date ='{appointment_date}' "
                   f"AND appointment_time NOT NULL")
    free_time = cursor.fetchall()
    connection.close()
    for x in free_time:
        occupied_time = x[0]
        if occupied_time in all_appointment_time:
            all_appointment_time.remove(occupied_time)
    return all_appointment_time


def restoring_user_date_for_sql_query(clients_date):
    cut_day = clients_date[0:2]
    cut_month = clients_date[3:5]
    year = datetime.date.today().year
    real_date_for_sql = f'{year}-{cut_month}-{cut_day}'
    return real_date_for_sql
