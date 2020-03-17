# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class BotAuthentication(models.Model):
    user = models.ForeignKey('User', models.DO_NOTHING)
    code = models.CharField(unique=True, max_length=5)
    creation_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'bot_authentication'


class DailyStatistics(models.Model):
    sensor = models.ForeignKey('Sensor', models.DO_NOTHING)
    value = models.CharField(max_length=45)
    day = models.DateField()

    class Meta:
        managed = False
        db_table = 'daily_statistics'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class HourlyStatistics(models.Model):
    sensor = models.ForeignKey('Sensor', models.DO_NOTHING)
    value = models.CharField(max_length=45)
    time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'hourly_statistics'


class House(models.Model):
    name = models.CharField(max_length=45, blank=True, null=True)
    additional_security = models.IntegerField()
    mac_address = models.CharField(db_column='MAC_address', max_length=12, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'house'


class Location(models.Model):
    id = models.IntegerField(primary_key=True)
    location = models.CharField(max_length=45)

    class Meta:
        managed = False
        db_table = 'location'


class LoginInfo(models.Model):
    user = models.ForeignKey('User', models.DO_NOTHING)
    date = models.DateTimeField()
    ip_address = models.CharField(max_length=45, blank=True, null=True)
    device = models.CharField(max_length=45, blank=True, null=True)
    browser = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'login_info'


class MonthlyStatistics(models.Model):
    sensor = models.ForeignKey('Sensor', models.DO_NOTHING)
    value = models.CharField(max_length=45)
    mounth = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'monthly_statistics'


class Notification(models.Model):
    house = models.ForeignKey(House, models.DO_NOTHING)
    notification_type = models.ForeignKey('NotificationType', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'notification'


class NotificationType(models.Model):
    message = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'notification_type'


class OldPassword(models.Model):
    user = models.ForeignKey('User', models.DO_NOTHING)
    password = models.CharField(max_length=45)

    class Meta:
        managed = False
        db_table = 'old_password'


class Password(models.Model):
    user = models.ForeignKey('User', models.DO_NOTHING)
    password = models.CharField(max_length=45)
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'password'


class Permission(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey('User', models.DO_NOTHING)
    house = models.ForeignKey(House, models.DO_NOTHING)
    close_valve = models.IntegerField()
    add_sensor = models.IntegerField()
    delete_sensor = models.IntegerField()
    delete_user = models.IntegerField()
    add_user = models.IntegerField()
    edit_sensors = models.IntegerField()
    edit_house_users = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'permission'


class ProfileSettings(models.Model):
    user_id = models.IntegerField(unique=True)
    language = models.CharField(max_length=3)
    users = models.ForeignKey('User', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'profile_settings'


class Sensor(models.Model):
    type = models.ForeignKey('SensorType', models.DO_NOTHING, db_column='type')
    location = models.ForeignKey(Location, models.DO_NOTHING, db_column='location')
    valve = models.ForeignKey('Valve', models.DO_NOTHING, db_column='valve')
    name = models.CharField(max_length=15)
    house = models.ForeignKey(House, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'sensor'


class SensorState(models.Model):
    sensor = models.OneToOneField(Sensor, models.DO_NOTHING)
    active = models.IntegerField()
    battery = models.IntegerField(blank=True, null=True)
    last_seen = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sensor_state'


class SensorType(models.Model):
    type = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sensor_type'


class TelegramBot(models.Model):
    user = models.ForeignKey('User', models.DO_NOTHING)
    chat_id = models.IntegerField(blank=True, null=True)
    enabled = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'telegram_bot'


class User(models.Model):
    name = models.CharField(max_length=45)
    surname = models.CharField(max_length=45)
    email = models.CharField(unique=True, max_length=45)
    number = models.CharField(max_length=45, blank=True, null=True)
    active = models.IntegerField(blank=True, null=True)
    suspended = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    deleted = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)
    last_login = models.DateTimeField(blank=True, null=True)
    lock_count = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'user'


class UserHasHouse(models.Model):
    user = models.OneToOneField(User, models.DO_NOTHING, primary_key=True)
    house = models.ForeignKey(House, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'user_has_house'
        unique_together = (('user', 'house'),)


class Valve(models.Model):
    location = models.ForeignKey(Location, models.DO_NOTHING, db_column='location')
    type = models.CharField(max_length=45)
    name = models.CharField(max_length=45)
    closed = models.IntegerField()
    active = models.IntegerField()
    house = models.ForeignKey(House, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'valve'


class ValveLog(models.Model):
    user = models.ForeignKey(User, models.DO_NOTHING)
    sensor = models.ForeignKey(Sensor, models.DO_NOTHING)
    valve = models.ForeignKey(Valve, models.DO_NOTHING)
    closed_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'valve_log'
