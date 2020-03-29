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


def create_valve(location, valve_name, house_id, valve_type, uniq_token):
    with connection.cursor() as cursor:
        cursor.execute("INSERT INTO valve(location, name, house_id, type, uniq_token) VALUES(%s, %s, %s, %s, %s)",
                       [location, valve_name, house_id, valve_type, uniq_token])
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


def get_house_sensors(house_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, location, name, house_id, type, valve FROM sensor WHERE house_id=%s", [house_id])
        sensors = [
            {'id': col1, 'location': col2, 'name': col3, 'house_id': col4, 'type': col5, "valve": col6, }
            for (col1, col2, col3, col4, col5, col6) in cursor.fetchall()]
        return sensors


def get_house_valves(house_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, location, name, house_id, type, closed, last_updated FROM valve WHERE house_id=%s",
                       [house_id])
        valves = [
            {'id': col1, 'location': col2, 'name': col3, 'house_id': col4, 'type': col5, "closed": col6,
             'last_updated': col7} for
            (col1, col2, col3, col4, col5, col6, col7) in cursor.fetchall()]
        return valves


def get_house_valves_update(house_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, closed, last_updated FROM valve WHERE house_id=%s",
                       [house_id])
        valves = cursor.fetchall()
        return valves


def get_house_sensors_update(house_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, closed, last_updated FROM valve WHERE house_id=%s",
                       [house_id])
        sensors = cursor.fetchall()
        return sensors


def get_locations():
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, location FROM location")
        locations = cursor.fetchall()
        return locations


def create_telegram(username, house_id, user_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT house_id FROM telegram_bot WHERE auth_user_id=%s AND house_id=%s", [user_id, house_id])
        if not cursor.fetchone():
            cursor.execute("INSERT into telegram_bot(nickname, house_id, auth_user_id) VALUES(%s, %s, %s)",
                       [username, house_id, user_id])


def delete_telegram(username, house_id):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM telegram_bot WHERE nickname=%s AND house_id=%s", [username, house_id])


def get_telegram_users(house_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT telegram_bot.auth_user_id, auth_user.first_name, auth_user.last_name, "
                       "telegram_bot.nickname "
                       "FROM telegram_bot "
                       "INNER JOIN auth_user "
                       "ON auth_user.id=telegram_bot.auth_user_id "
                       "WHERE house_id=%s", [house_id])
        return cursor.fetchall()


def get_house_users(house_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT auth_user_id, first_name, last_name "
                       "FROM auth_user_has_house "
                       "INNER JOIN auth_user "
                       "ON auth_user_has_house.auth_user_id=auth_user.id  "
                       "WHERE auth_user_has_house.house_id=%s", [house_id])
        return cursor.fetchall()


def delete_valve(valve_id):
    with connection.cursor() as cursor:
        #implement delete from valve log
        #implement delete all sensors related to valve or restrict if exist
        cursor.execute("DELETE FROM valve WHERE id=%s", [valve_id])
