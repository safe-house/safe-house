from django.db import connection
import time


def save_token(user_id, token):
    with connection.cursor() as cursor:
        cursor.execute("insert into authentification (auth_user_id, code, expire_at)"
                       " VALUES (%s, %s, %s)", [user_id, token, time.strftime('%Y-%m-%d %H:%M:%S')])


def check_token(user_id, token):
    with connection.cursor() as cursor:
        cursor.execute("select auth_user_id, code, expire_at from authentification "
                       "where auth_user_id=%s and code=%s",
                       [user_id, token])
        row = cursor.fetchone()
        return row


def activate_user(user_id):
    with connection.cursor() as cursor:
        cursor.execute("update auth_user set is_active=1 where id=%s", [user_id])
        cursor.execute("DELETE FROM authentification where auth_user_id=%s", [user_id])



