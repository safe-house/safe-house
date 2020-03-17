from django.db import connection
import time


def create_user(self):
    with connection.cursor() as cursor:
        cursor.execute("CALL CREATE_USER( %s,  %s,  %s,  %s,  %s)", self)


def login(email, password):
    with connection.cursor() as cursor:
        cursor.execute("select user.id from user "
                       "INNER JOIN password on user.id = password.user_id"
                       " WHERE email = %s and password= %s", [email, password])
        row = cursor.fetchone()
        return row


def activate_user(email, password):
    with connection.cursor() as cursor:
        cursor.execute("select user.id from user "
                       "INNER JOIN password on user.id = password.user_id"
                       " WHERE email = %s and password= %s", [email, password])


def confirmation_creation(user_id):
    with connection.cursor() as cursor:
        cursor.execute("insert into authentification (auth_user_id, code, expire_at)"
                       " VALUES (%s, %s, %s)", [user_id, "FFF555", time.strftime('%Y-%m-%d %H:%M:%S')])