import mysql.connector

database = mysql.connector.connect(
            host="localhost",
            port="3306",
            user="safehouse",
            passwd="safehouse2020",
            database="safehouse1",
            auth_plugin='mysql_native_password'
        )


def check_username(username):
    try:
        cursor = database.cursor()
        sql = "SELECT nickname FROM telegram_bot WHERE nickname=%s"
        cursor.execute(sql, [username])
        database.close()
        return cursor.fetchall()
    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))