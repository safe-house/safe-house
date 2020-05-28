from django.db import connection
import datetime


def save_token(user_id, token):
    with connection.cursor() as cursor:
        cursor.execute("INSERT INTO authentication (auth_user_id, code, expire_at)"
                       " VALUES (%s, %s, %s)", [user_id, token, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')])


def check_token(user_id, token):
    with connection.cursor() as cursor:
        cursor.execute("SELECT auth_user_id, code, expire_at FROM authentication "
                       "WHERE auth_user_id=%s AND code=%s",
                       [user_id, token])
        row = cursor.fetchone()
        return row


def create_user_invitation_token(house_id, token):
    with connection.cursor() as cursor:
        cursor.execute("INSERT INTO house_authentication (code, expire_at, house_id)"
                       "VALUES (%s, %s, %s)",
                       [token, (datetime.datetime.now() + datetime.timedelta(minutes=10)).strftime('%Y-%m-%d %H:%M:%S'),
                        house_id])


def delete_user_invitation_token(house_id):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM house_authentication WHERE house_id=%s", [house_id])


def get_invitation_token(house_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT code FROM house_authentication WHERE house_id=%s", [house_id])
        row = cursor.fetchone()
        return row


def activate_user(user_id):
    with connection.cursor() as cursor:
        cursor.execute("UPDATE auth_user SET is_active=1 WHERE id=%s", [user_id])
        cursor.execute("DELETE FROM authentication WHERE auth_user_id=%s", [user_id])


def create_valve(location, valve_name, house_id, valve_type, uniq_token):
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO valve(location, name, house_id, type, uniq_token) "
            "VALUES(%s, %s, %s, %s, %s)",
            [location, valve_name, house_id, valve_type, uniq_token])
    valve_id = cursor.lastrowid
    return valve_id


def create_sensor(sensor_name, house_id, sensor_type, valve_id, code, last_updated, value):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id FROM sensor where sensor_code=%s", [code])
        sensor = cursor.fetchone()
        if sensor:
            cursor.execute("UPDATE sensor_state SET last_seen=%s, last_data=%s WHERE sensor_id=%s",
                           [sensor[0], last_updated, value])
        else:
            cursor.execute("INSERT INTO sensor(name, house_id, type, valve, sensor_code) VALUES(%s, %s, %s, %s, %s)",
                           [sensor_name, house_id, sensor_type, valve_id, code])
            sensor_id = cursor.lastrowid
            cursor.execute("INSERT INTO sensor_state(sensor_id, last_seen, last_data) VALUES(%s, %s, %s)",
                           [sensor_id, last_updated, value])


def create_house():
    with connection.cursor() as cursor:
        cursor.execute("INSERT INTO house(name) VALUES(%s)",
                       ["house"])
        house_id = cursor.lastrowid
        return house_id


def set_default_house(user_id, house_id):
    with connection.cursor() as cursor:
        cursor.execute("INSERT INTO chose_house(user_id, house_id) VALUES(%s, %s)", [user_id, house_id])


def create_user_has_house(user_id, house_id, is_admin):
    with connection.cursor() as cursor:
        cursor.execute("INSERT INTO auth_user_has_house(auth_user_id, house_id, is_admin) VALUES(%s, %s,  %s)",
                       [user_id, house_id, is_admin])


def check_user_preferences(user_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT is_admin FROM auth_user_has_house where auth_user_id=%s", [user_id])
        preference = cursor.fetchone()
        return preference


def delete_user_has_house(user_id, house_id):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM chose_house WHERE user_id=%s AND house_id=%s",
                       [user_id, house_id])
        cursor.execute("DELETE FROM auth_user_has_house WHERE auth_user_id=%s AND house_id=%s",
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
        cursor.execute("SELECT sensor.id, name, valve, last_seen, last_data FROM sensor "
                       "INNER JOIN sensor_state ON sensor.id=sensor_state.sensor_id "
                       "WHERE sensor.house_id=%s", [house_id])
        return cursor.fetchall()


def get_house_valves(house_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, location, name, house_id, type, closed, last_updated, active, uniq_token "
                       "FROM valve WHERE house_id=%s AND active=1",
                       [house_id])
        return cursor.fetchall()


def get_house_valves_all(house_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, location, name, house_id, type, closed, last_updated, active, uniq_token "
                       "FROM valve WHERE house_id=%s",
                       [house_id])
        return cursor.fetchall()


def get_house_valves_update(house_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, closed, last_updated FROM valve WHERE house_id=%s",
                       [house_id])
        valves = cursor.fetchall()
        return valves


def get_house_sensors_update(house_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, last_updated FROM valve WHERE house_id=%s",
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
        cursor.execute("SELECT auth_user_id, first_name, last_name, email, is_active "
                       "FROM auth_user_has_house "
                       "INNER JOIN auth_user "
                       "ON auth_user_has_house.auth_user_id=auth_user.id  "
                       "WHERE auth_user_has_house.house_id=%s", [house_id])
        return cursor.fetchall()


def delete_valve(valve_id):
    with connection.cursor() as cursor:
        # implement deletion of sensors statistics
        cursor.execute("DELETE FROM valve_log WHERE valve_id=%s", [valve_id])
        cursor.execute("SELECT id FROM sensor WHERE valve=%s", [valve_id])
        sensors = cursor.fetchall()
        for sensor in sensors:
            print(sensor[0])
            cursor.execute("DELETE FROM sensor_state WHERE sensor_id=%s", [sensor[0]])
        cursor.execute("DELETE FROM sensor WHERE valve=%s", [valve_id])
        cursor.execute("DELETE FROM valve WHERE id=%s", [valve_id])


def activate_valve(token):
    with connection.cursor() as cursor:
        cursor.execute("UPDATE valve SET active=1, last_updated=current_timestamp() WHERE uniq_token=%s", [token])
        cursor.execute("SELECT id, house_id FROM valve WHERE uniq_token=%s", [token])
        return cursor.fetchone()


def update_valve(token, closed):
    with connection.cursor() as cursor:
        cursor.execute("UPDATE valve SET closed=%s, last_updated=current_timestamp() WHERE uniq_token=%s",
                       [closed, token])


def update_sensor(last_updated, value, code):
    with connection.cursor() as cursor:
        cursor.execute("SELECT id FROM sensor where sensor_code=%s", [code])
        sensor = cursor.fetchone()
        print(sensor[0])
        if sensor:
            cursor.execute("UPDATE sensor_state SET last_seen=%s, last_data=%s WHERE sensor_id=%s",
                           [last_updated, value, sensor[0]])


def get_chat_id(token):
    with connection.cursor() as cursor:
        cursor.execute("SELECT house_id FROM valve where uniq_token=%s", [token])
        house = cursor.fetchone()
        cursor.execute("SELECT chat_id FROM telegram_bot where house_id=%s", [house[0]])
        return cursor.fetchall()


def update_user(name, surname, user_id):
    with connection.cursor() as cursor:
        cursor.execute("UPDATE auth_user SET first_name=%s, last_name=%s where id=%s", [name, surname, user_id])


def delete_user(user_id, house_id):
    delete_telegram_by_user_id(user_id, house_id)
    delete_messenger_user(user_id)
    delete_profile_settings(user_id)
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM authentication WHERE auth_user_id=%s", [user_id])
    delete_user_has_house(user_id, house_id)


def delete_telegram_by_user_id(user_id, house_id):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM telegram_bot WHERE auth_user_id=%s AND house_id=%s", [user_id, house_id])


def delete_profile_settings(user_id):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM profile_settings WHERE auth_user_id=%s", [user_id])


def create_messenger_user(user_id, messenger_id, house_id):
    with connection.cursor() as cursor:
        cursor.execute("INSERT INTO messenger(auth_user_id, messenger_id, house_id) values(%s, %s, %s)", [user_id, messenger_id, house_id])


def delete_messenger_user(user_id):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM messenger WHERE auth_user_id=%s", [user_id])


def get_messenger_users_by_house(house_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT messenger.auth_user_id, auth_user.first_name, auth_user.last_name "
                       "FROM messenger "
                       "INNER JOIN auth_user "
                       "ON auth_user.id=telegram_bot.auth_user_id "
                       "WHERE house_id=%s", [house_id])
        return cursor.fetchall()