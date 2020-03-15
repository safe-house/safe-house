from django.db import connection


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
