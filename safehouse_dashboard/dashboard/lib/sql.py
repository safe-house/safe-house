from django.db import connection
import time


def save_token(user_id, token):
    with connection.cursor() as cursor:
        cursor.execute("INSERT INTO authentication (auth_user_id, code, expire_at)"
                       " VALUES (%s, %s, %s)", [user_id, token, time.strftime('%Y-%m-%d %H:%M:%S')])


def check_token(user_id, token):
    with connection.cursor() as cursor:
        cursor.execute("SELECT auth_user_id, code, expire_at FROM authentication "
                       "WHERE auth_user_id=%s AND code=%s",
                       [user_id, token])
        row = cursor.fetchone()
        return row


def activate_user(user_id):
    with connection.cursor() as cursor:
        cursor.execute("UPDATE auth_user SET is_active=1 WHERE id=%s", [user_id])
        cursor.execute("DELETE FROM authentication WHERE auth_user_id=%s", [user_id])


def create_valve(location, valve_name, house_id, valve_type):
    with connection.cursor() as cursor:
        cursor.execute("INSERT INTO valve(location, name, house_id, type) VALUES(%s, %s, %s, %s)",
                       [location, valve_name, house_id, valve_type])
    valve_id = cursor.lastrowid
    return valve_id


def create_sensor(location, sensor_name, house_id, sensor_type, valve_id):
    with connection.cursor() as cursor:
        cursor.execute("INSERT INTO sensor(location, name, house_id, type, valve) VALUES(%s, %s, %s, %s, %s)",
                       [location, sensor_name, house_id, sensor_type, valve_id])
        sensor_id = cursor.lastrowid
        cursor.execute("INSERT INTO sensor_state(sensor_id) VALUES(%s)",
                       [sensor_id])


def create_house():
    with connection.cursor() as cursor:
        cursor.execute("INSERT INTO house(name) VALUES(%s)",
                       ["house"])
        house_id = cursor.lastrowid
        return house_id


def set_default_house(user_id, house_id):
    with connection.cursor() as cursor:
        cursor.execute("INSERT INTO chose_house(user_id, house_id) VALUES(%s, %s)", [user_id, house_id])


def create_user_has_house(user_id, house_id):
    with connection.cursor() as cursor:
        cursor.execute("INSERT INTO auth_user_has_house(auth_user_id, house_id) VALUES(%s, %s)",
                       [user_id, house_id])


def get_default_house(user_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT house_id "
                       "FROM chose_house WHERE user_id=%s",
                       [user_id])
        house_id = cursor.fetchone()
        return house_id


def get_house_sensors(user_id):
    with connection.cursor() as cursor:
        house_id = get_default_house(user_id)
        cursor.execute("SELECT id, location, name, house_id, type, valve FROM sensor WHERE house_id=%s", [house_id[0]])
        sensors = cursor.fetchall()
        return sensors


def get_house_valves(user_id):
    with connection.cursor() as cursor:
        house_id = get_default_house(user_id)
        cursor.execute("SELECT id, location, name, house_id, type, closed, last_updated FROM valve WHERE house_id=%s",
                       [house_id[0]])
        valves = cursor.fetchall()
        return valves


def get_house_valves_update(house_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, closed, last_updated FROM valve WHERE house_id=%s",
                       [house_id[0]])
        valves = cursor.fetchall()
        return valves


def get_house_sensors_update(house_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, closed, last_updated FROM valve WHERE house_id=%s",
                       [house_id[0]])
        sensors = cursor.fetchall()
        return sensors
