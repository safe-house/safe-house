import mysql.connector


def database(query, params):
    try:
        connection = mysql.connector.connect(
            host="localhost",
            port="3306",
            user="safehouse",
            passwd="safehouse2020",
            database="safehouse1",
            auth_plugin='mysql_native_password'
        )
        cursor = connection.cursor()
        print(str(params))
        cursor.execute(query, params)
        return cursor.fetchall()
    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def check_username(username):
    sql = "SELECT nickname FROM telegram_bot WHERE nickname=%s"
    return database(sql, [username])
