# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desidered behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class CmActualite(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    message = models.CharField(max_length=555)
    nom = models.CharField(max_length=255)
    personne_concernee = models.ForeignKey('CmUtilisateur', models.DO_NOTHING)
    lien = models.CharField(max_length=555)
    date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'CM_actualite'


class CmContestation(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    nom = models.CharField(max_length=255)
    contenu = models.CharField(max_length=555)

    class Meta:
        managed = False
        db_table = 'CM_contestation'


class CmDefi(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    prive = models.BooleanField()
    etat = models.CharField(max_length=2)
    date_acceptation = models.DateTimeField(blank=True, null=True)
    date_execution = models.DateTimeField(blank=True, null=True)
    expire = models.BooleanField()
    challengeur = models.ForeignKey('CmUtilisateur', models.DO_NOTHING)
    contestation = models.ForeignKey(CmContestation, models.DO_NOTHING, blank=True, null=True)
    defieur = models.ForeignKey('CmUtilisateur', models.DO_NOTHING)
    libelle = models.ForeignKey('CmLibelleDefi', models.DO_NOTHING)
    date_validation = models.DateTimeField(blank=True, null=True)
    warning_analyse = models.BooleanField()
    warning_triche = models.BooleanField()
    enjeu_perso = models.CharField(max_length=500)
    date_envoie = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'CM_defi'


class CmDefiPreuve(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    defi = models.ForeignKey(CmDefi, models.DO_NOTHING)
    preuve = models.ForeignKey('CmPreuve', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'CM_defi_preuve'
        unique_together = (('defi', 'preuve'),)


class CmDemandeami(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    active = models.BooleanField()
    auteur = models.ForeignKey('CmUtilisateur', models.DO_NOTHING)
    recepteur = models.ForeignKey('CmUtilisateur', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'CM_demandeami'


class CmLibelleDefi(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    nom = models.CharField(max_length=255)
    description = models.CharField(max_length=5000)
    auteur = models.ForeignKey('CmUtilisateur', models.DO_NOTHING)
    recompense = models.ForeignKey('CmRecompense', models.DO_NOTHING)
    sous_theme = models.ForeignKey('CmSousTheme', models.DO_NOTHING)
    theme = models.ForeignKey('CmTheme', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'CM_libelle_defi'


class CmLibelleQuete(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    objectif = models.CharField(max_length=255)
    description = models.CharField(max_length=5000)
    auteur = models.ForeignKey('CmUtilisateur', models.DO_NOTHING)
    recompense = models.ForeignKey('CmRecompense', models.DO_NOTHING)
    theme = models.ForeignKey('CmTheme', models.DO_NOTHING)
    duree = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'CM_libelle_quete'


class CmLibelleQueteDefis(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    libelle_quete = models.ForeignKey(CmLibelleQuete, models.DO_NOTHING)
    libelle_defi = models.ForeignKey(CmLibelleDefi, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'CM_libelle_quete_defis'
        unique_together = (('libelle_quete', 'libelle_defi'),)


class CmMaj(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'CM_maj'


class CmNationalite(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    pays = models.CharField(max_length=255)
    drapeau = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'CM_nationalite'


class CmNotification(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    type = models.CharField(max_length=2)
    message = models.CharField(max_length=1000)
    lien = models.CharField(max_length=500)
    active = models.BooleanField()
    vue = models.BooleanField()
    auteur = models.ForeignKey('CmUtilisateur', models.DO_NOTHING)
    recepteur = models.ForeignKey('CmUtilisateur', models.DO_NOTHING)
    date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'CM_notification'


class CmPhoto(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    nom = models.CharField(max_length=255)
    thumbnail = models.CharField(max_length=100)
    image = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'CM_photo'


class CmPreuve(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    nom = models.CharField(max_length=255)
    fichier = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'CM_preuve'


class CmPropositionDefi(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    nom = models.CharField(max_length=255)
    description = models.CharField(max_length=5000)
    auteur = models.ForeignKey('CmUtilisateur', models.DO_NOTHING)
    etat = models.CharField(max_length=2)

    class Meta:
        managed = False
        db_table = 'CM_proposition_defi'


class CmQuete(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    prive = models.BooleanField()
    active = models.BooleanField()
    etat = models.CharField(max_length=2)
    date_fin = models.DateTimeField(blank=True, null=True)
    expire = models.BooleanField()
    challengeur = models.ForeignKey('CmUtilisateur', models.DO_NOTHING)
    libelle = models.ForeignKey(CmLibelleQuete, models.DO_NOTHING)
    date_debut = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'CM_quete'


class CmRecompense(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    nom = models.CharField(max_length=255)
    points = models.IntegerField()
    goodies = models.BooleanField()
    goodies_description = models.CharField(max_length=500)
    decoration = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'CM_recompense'


class CmSignalement(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    motif = models.CharField(max_length=555)
    nom = models.CharField(max_length=255)
    defi = models.ForeignKey(CmDefi, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'CM_signalement'


class CmSousTheme(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    nom = models.CharField(max_length=255)
    theme = models.ForeignKey('CmTheme', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'CM_sous_theme'


class CmTeam(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    nom = models.CharField(max_length=255)
    photo_team = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'CM_team'


class CmTeamMembres(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    team = models.ForeignKey(CmTeam, models.DO_NOTHING)
    utilisateur = models.ForeignKey('CmUtilisateur', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'CM_team_membres'
        unique_together = (('team', 'utilisateur'),)


class CmTheme(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    nom = models.CharField(max_length=255)
    descritption = models.CharField(max_length=255)
    couleur = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'CM_theme'


class CmUtilisateur(models.Model):
    user_ptr = models.ForeignKey('AuthUser', models.DO_NOTHING, primary_key=True)
    age = models.IntegerField()
    score_absolu = models.IntegerField()
    score_race = models.IntegerField()
    score_cuisine = models.IntegerField()
    score_sport = models.IntegerField()
    score_extreme = models.IntegerField()
    score_social_environnement = models.IntegerField()
    score_autre = models.IntegerField()
    score_arts = models.IntegerField()
    nom_entier = models.CharField(max_length=255)
    info = models.CharField(max_length=255)
    email_valide = models.BooleanField()
    latitude = models.CharField(max_length=255)
    longitude = models.CharField(max_length=255)
    position = models.BooleanField()
    pa = models.ForeignKey(CmPhoto, models.DO_NOTHING)
    pp = models.ForeignKey(CmPhoto, models.DO_NOTHING)
    derniere_connexion = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'CM_utilisateur'


class CmUtilisateurAmis(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    from_utilisateur = models.ForeignKey(CmUtilisateur, models.DO_NOTHING)
    to_utilisateur = models.ForeignKey(CmUtilisateur, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'CM_utilisateur_amis'
        unique_together = (('from_utilisateur', 'to_utilisateur'),)


class AuthGroup(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    name = models.CharField(unique=True, max_length=80)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)
    name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()
    username = models.CharField(unique=True, max_length=30)

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class CeleryTaskmeta(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    task_id = models.CharField(unique=True, max_length=255)
    status = models.CharField(max_length=50)
    result = models.TextField(blank=True, null=True)
    date_done = models.DateTimeField()
    traceback = models.TextField(blank=True, null=True)
    hidden = models.BooleanField()
    meta = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'celery_taskmeta'


class CeleryTasksetmeta(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    taskset_id = models.CharField(unique=True, max_length=255)
    result = models.TextField()
    date_done = models.DateTimeField()
    hidden = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'celery_tasksetmeta'


class DjangoAdminLog(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    action_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoCronCronjoblog(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    code = models.CharField(max_length=64)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_success = models.BooleanField()
    ran_at_time = models.TimeField(blank=True, null=True)
    message = models.TextField()

    class Meta:
        managed = False
        db_table = 'django_cron_cronjoblog'


class DjangoMigrations(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
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


class DjceleryCrontabschedule(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    minute = models.CharField(max_length=64)
    hour = models.CharField(max_length=64)
    day_of_week = models.CharField(max_length=64)
    day_of_month = models.CharField(max_length=64)
    month_of_year = models.CharField(max_length=64)

    class Meta:
        managed = False
        db_table = 'djcelery_crontabschedule'


class DjceleryIntervalschedule(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    every = models.IntegerField()
    period = models.CharField(max_length=24)

    class Meta:
        managed = False
        db_table = 'djcelery_intervalschedule'


class DjceleryPeriodictask(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    name = models.CharField(unique=True, max_length=200)
    task = models.CharField(max_length=200)
    args = models.TextField()
    kwargs = models.TextField()
    queue = models.CharField(max_length=200, blank=True, null=True)
    exchange = models.CharField(max_length=200, blank=True, null=True)
    routing_key = models.CharField(max_length=200, blank=True, null=True)
    expires = models.DateTimeField(blank=True, null=True)
    enabled = models.BooleanField()
    last_run_at = models.DateTimeField(blank=True, null=True)
    total_run_count = models.PositiveIntegerField()
    date_changed = models.DateTimeField()
    description = models.TextField()
    crontab = models.ForeignKey(DjceleryCrontabschedule, models.DO_NOTHING, blank=True, null=True)
    interval = models.ForeignKey(DjceleryIntervalschedule, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'djcelery_periodictask'


class DjceleryPeriodictasks(models.Model):
    ident = models.SmallIntegerField(primary_key=True)
    last_update = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'djcelery_periodictasks'


class DjceleryTaskstate(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    state = models.CharField(max_length=64)
    task_id = models.CharField(unique=True, max_length=36)
    name = models.CharField(max_length=200, blank=True, null=True)
    tstamp = models.DateTimeField()
    args = models.TextField(blank=True, null=True)
    kwargs = models.TextField(blank=True, null=True)
    eta = models.DateTimeField(blank=True, null=True)
    expires = models.DateTimeField(blank=True, null=True)
    result = models.TextField(blank=True, null=True)
    traceback = models.TextField(blank=True, null=True)
    runtime = models.FloatField(blank=True, null=True)
    retries = models.IntegerField()
    hidden = models.BooleanField()
    worker = models.ForeignKey('DjceleryWorkerstate', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'djcelery_taskstate'


class DjceleryWorkerstate(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    hostname = models.CharField(unique=True, max_length=255)
    last_heartbeat = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'djcelery_workerstate'


class DjkombuMessage(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    visible = models.BooleanField()
    sent_at = models.DateTimeField(blank=True, null=True)
    payload = models.TextField()
    queue = models.ForeignKey('DjkombuQueue', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'djkombu_message'


class DjkombuQueue(models.Model):
    id = models.IntegerField(primary_key=True)  # AutoField?
    name = models.CharField(unique=True, max_length=200)

    class Meta:
        managed = False
        db_table = 'djkombu_queue'
