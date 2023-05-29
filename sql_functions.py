from datetime import datetime, date
from service.models import (
    Appointment, Client, Master, Service, User, Feedback
    )
import datetime
import sqlite3

BASE = 'db.sqlite3'


def sql_register_new_user(tg_id, name, phone):
    time_create = datetime.datetime.now()

    # Создать нового пользователя Django
    try:
        user = User.objects.get(username=str(tg_id))
    except User.DoesNotExist:
        user = User.objects.create_user(username=str(tg_id))

    # Создать новый объект Client
    client = Client(
        user=user,
        tg_id=tg_id,
        name=name,
        phonenumber=phone,
        time_create=time_create
    )

    # Сохраняем объект Client в базе данных
    client.save()


def sql_get_user_data(tg_id) -> dict:
    conn = sqlite3.connect(BASE)
    cur = conn.cursor()
    exec_text = f"SELECT * FROM 'service_client' WHERE tg_id is '{tg_id}'"
    cur.execute(exec_text)
    result = cur.fetchone()
    conn.close()

    if isinstance(result, type(None)):
        return False

    formated_result = {
        'id': result[0],
        'name': result[1],
        'phone': result[2],
        'tg_id': result[5],
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
    time_create = datetime.datetime.now()

    # Находим клиента по tg_id
    client = Client.objects.get(tg_id=tg_id)

    # Создаем новый объект Appointment
    appointment = Appointment(
        appointment_date=meet_date,
        appointment_time=meet_time,
        time_create=time_create,
        client=client
    )

    if master_id:
        # Находим мастера по master_id
        master = Master.objects.get(id=master_id)
        appointment.master = master
    else:
        # Находим услугу по service_id
        service = Service.objects.get(id=service_id)
        appointment.service = service

    # Сохраняем объект Appointment в базе данных
    appointment.save()


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


def get_free_time_for_master(client_date, master_id):
    appointment_date = restoring_user_date_for_sql_query(client_date)
    all_appointment_time = [
        '10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:00',
        '13:30', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30',
        '17:00', '17:30', '18:00', '18:30', '19:00', '19:30', '20:00',
        '20:30'
    ]
    connection = sqlite3.connect(BASE)
    cursor = connection.cursor()
    cursor.execute(f"SELECT appointment_time FROM service_appointment "
                   f"WHERE master_id={master_id} "
                   f"AND appointment_date ='{appointment_date}' "
                   f"AND appointment_time NOT NULL")
    free_time = cursor.fetchall()
    connection.close()
    for x in free_time:
        occupied_time = x[0]
        if occupied_time in all_appointment_time:
            all_appointment_time.remove(occupied_time)
    return all_appointment_time


def get_free_time_for_procedure(client_date):
    appointment_date = restoring_user_date_for_sql_query(client_date)
    all_appointment_time = [
        '10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:00',
        '13:30', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30',
        '17:00', '17:30', '18:00', '18:30', '19:00', '19:30', '20:00',
        '20:30'
    ]
    connection = sqlite3.connect(BASE)
    cursor = connection.cursor()
    cursor.execute(f"""SELECT appointment_time FROM service_appointment
                       WHERE appointment_date='{appointment_date}'
                       GROUP BY appointment_time
                       HAVING COUNT(appointment_date)>1""""")
    free_time = cursor.fetchall()
    connection.close()
    for x in free_time:
        occupied_time = x[0]
        if occupied_time in all_appointment_time:
            all_appointment_time.remove(occupied_time)
    return all_appointment_time


def get_past_appointment(client_id):
    connection = sqlite3.connect(BASE)
    cursor = connection.cursor()

    today = date.today()
    query = '''
    SELECT * FROM service_appointment
    WHERE client_id = ? AND date(appointment_date) < date(?)
    ORDER BY appointment_date DESC
    LIMIT 1
    '''
    cursor.execute(query, (client_id, today))
    appointment = cursor.fetchone()

    connection.close()
    return appointment[0] if appointment else False


def sql_add_feedback(appointment_id, client_id, feedback_text):
    appointment = Appointment.objects.get(id=appointment_id)
    client = Client.objects.get(id=client_id)
    feedback = Feedback(appointment=appointment, client=client, feedback_text=feedback_text)
    feedback.save()
    return feedback
