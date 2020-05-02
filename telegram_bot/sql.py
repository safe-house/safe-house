import mysql.connector
import constants


def database(query, params, fetch=True):
    try:
        connection = mysql.connector.connect(
            host=constants.HOST,
            port=constants.PORT,
            user=constants.USER,
            passwd=constants.PASSWORD,
            database=constants.DATABASE,
            auth_plugin=constants.AUTH_PLUGIN
        )
        cursor = connection.cursor()
        cursor.execute(query, params)
        if fetch:
            return cursor.fetchall()
        else:
            connection.commit()
    except mysql as err:
        print("Something went wrong: {}".format(err))
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def check_username(username):
    sql = "SELECT nickname FROM telegram_bot WHERE nickname=%s"
    return database(sql, [username])


def sensors_state(username):
    sql = "SELECT house_id FROM telegram_bot WHERE nickname=%s"
    result = database(sql, [username])
    sql1 = "SELECT sensor.id, name, valve, last_seen, last_data FROM sensor " \
           "INNER JOIN sensor_state ON sensor.id=sensor_state.sensor_id " \
           "WHERE sensor.house_id=%s"
    return database(sql1, [result[0][0]])


def insert_chat_id(chat_id, username):
    print(username, chat_id)
    sql = "UPDATE telegram_bot SET chat_id=%s WHERE nickname=%s"
    database(sql, [chat_id, username], False)
