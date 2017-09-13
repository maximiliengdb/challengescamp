# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.template.defaultfilters import default
from _datetime import date, datetime

now = datetime.now()
    
class Photo(models.Model):
    nom = models.CharField(max_length=255)
    thumbnail = models.ImageField(upload_to='image/thumbs/')
    image = models.ImageField(upload_to='image')
    
class Nationalite(models.Model):
    pays = models.CharField(max_length=255)
    drapeau = models.ImageField(upload_to='image/utilisateurs/drapeau')
    

class Utilisateur(User):
    
    position = models.BooleanField(default = False)
    derniere_connexion = models.DateTimeField(auto_now=False, default = now)
    latitude = models.CharField(max_length = 255, default= "0")
    longitude = models.CharField(max_length = 255, default= "0")
    
    email_valide = models.BooleanField(default = False)
    
    age = models.IntegerField(default = 0)
    score_absolu = models.IntegerField(default = 0)
    
    score_race = models.IntegerField(default = 0)
    
    score_cuisine = models.IntegerField(default = 0)
    score_sport = models.IntegerField(default = 0)
    score_extreme = models.IntegerField(default = 0)
    score_social_environnement = models.IntegerField(default = 0)
    score_autre = models.IntegerField(default = 0)
    score_arts = models.IntegerField(default = 0)
    
    pp = models.ForeignKey('Photo', related_name="pp", default = 1)
    pa = models.ForeignKey('Photo', related_name="pa", default = 2)
    
    nom_entier = models.CharField(max_length = 255, default="Sans Nom")
    info = models.CharField(max_length = 255, default="Sans description")
    
    amis = models.ManyToManyField('Utilisateur')
    
    def __str__(self):
        return self.username
    
    
class Team(models.Model):
    
    nom = models.CharField(max_length = 255, default="Sans Nom")
    photo_team = models.ImageField(upload_to='image/team/profil', null=True)
    
    membres = models.ManyToManyField('Utilisateur', related_name="user", default = None)
    
    def __str__(self):
        return self.nom
    
class Notification(models.Model):
    
    TYPE = (
        ('DA', "Demande d'ami"),
        ('D', 'Defi'),
        ('Q', 'Quête'),
        ('C', 'Contest'),
    )
    
    type= models.CharField(max_length=2, choices=TYPE, default='D')
    
    message = models.CharField(max_length=1000)
    lien = models.CharField(max_length=500)
    
    auteur = models.ForeignKey('Utilisateur' ,related_name="auteur")
    recepteur = models.ForeignKey('Utilisateur' ,related_name="recepteur")
    
    date = models.DateTimeField(auto_now=False, default = now) 
    
    active = models.BooleanField(default = True)
    vue = models.BooleanField(default = False)
    
    def __str__(self):
        return self.message
    
class DemandeAmi(models.Model):
    auteur = models.ForeignKey('Utilisateur' ,related_name="demandeur")
    recepteur = models.ForeignKey('Utilisateur' ,related_name="amidemande")
    
    active = models.BooleanField(default = True)
   
    def __str__(self):
        return self.recepteur.username + ' de la part de '+ self.auteur.username 
    
class Proposition_Defi (models.Model):       
    nom = models.CharField(max_length = 255, default="Sans Titre")
    description = models.CharField(max_length = 5000, default="Sans Titre")
    
    auteur = models.ForeignKey(Utilisateur)
    
    ETAT = (
        ('E', 'Envoyé'),
        ('D', 'Default'),
        ('V', 'Validé'),
        ('S', 'Signalé'),
    )
    
    etat = models.CharField(max_length=2, choices=ETAT, default='E')
    
    
    def __str__(self):
        return self.nom    

class Preuve(models.Model):
    nom = models.CharField(max_length=255)
    fichier = models.FileField(upload_to='defi/preuve', null = True)
    
    def __str__(self):
        return self.nom

class Contestation(models.Model):
    nom = models.CharField(max_length=255)
    contenu = models.CharField(max_length=555, default="Sans Motif")
    
    def __str__(self):
        return self.nom

class Signalement(models.Model):
    motif = models.CharField(max_length=555, default="Sans Motif")
    nom = models.CharField(max_length=255, default="Sans Nom")
    
    
    def __str__(self):
        return self.nom
    
class Recompense(models.Model):
    nom = models.CharField(max_length=255)
    decoration = models.CharField(max_length=255, default = "<span class='ti-bolt'> </span>")
    points = models.IntegerField(default = 0)
    goodies = models.BooleanField(default = False)
    goodies_description = models.CharField(max_length = 500, default = "Sans Goodies")
    
    def __str__(self):
        return self.nom

       
class Theme (models.Model):
    nom = models.CharField(max_length=255)
    descritption = models.CharField(max_length=255, default = " ")
    couleur = models.CharField(max_length=255)
    
    def __str__(self):
        return self.nom
    
class Sous_Theme(models.Model):
    nom = models.CharField(max_length=255)
    theme = models.ForeignKey(Theme)
    def __str__(self):
        return self.nom


class MapPoint(models.Model):
    
    x = models.CharField(max_length=255, default="rien")
    y = models.CharField(max_length=255, default="rien")
    id_osm = models.CharField(max_length=255, default="rien")
    nom = models.CharField(max_length=255, default="rien")
    attribut = models.CharField(max_length=855, default="rien")
    
    categorie = models.CharField(max_length = 255, default="rien")
    sous_categorie = models.CharField(max_length = 255, default="rien")
    
    def __str__(self):
        return self.id_osm
        
        
        
class Libelle_Defi (models.Model):
    
    nom = models.CharField(max_length = 255, default="Sans Titre")
    description = models.CharField(max_length = 5000, default="Sans Description")
    recompense = models.ForeignKey(Recompense)
    
    duree_acceptation = models.IntegerField(default = 1) 
    duree_execution = models.IntegerField(default = 1) 
    
    theme = models.ForeignKey(Theme, default = 1)
    sous_theme = models.ForeignKey(Sous_Theme, default = 1)
    
    auteur = models.ForeignKey(Utilisateur)
     
    def __str__(self):
        return self.nom
    
class Libelle_Quete (models.Model):
    
    theme = models.ForeignKey(Theme, default = 1)
    
    objectif = models.CharField(max_length = 255, default="Sans Titre")
    description = models.CharField(max_length = 5000, default="Sans Description")
    recompense = models.ForeignKey(Recompense)
    
    defis = models.ManyToManyField(Libelle_Defi)
    duree = models.IntegerField(default = 7)
    auteur = models.ForeignKey(Utilisateur)
     
    def __str__(self):
        return self.objectif
    
class Quete(models.Model):
    
    libelle = models.ForeignKey(Libelle_Quete)
    challengeur = models.ForeignKey(Utilisateur)
    
    prive = models.BooleanField(default = False)
    
    active = models.BooleanField(default = True)
    
    ETAT = (
        ('D', 'Default'),
        ('V', 'Validé'),
        ('S', 'Signalé'),
    )
    
    etat = models.CharField(max_length=2, choices=ETAT, default='D')
    
    date_debut = models.DateTimeField(auto_now=False, default = now)
    date_fin = models.DateTimeField(null = True)
    
    expire = models.BooleanField(default = False)
    
    def __str__(self):
        return self.libelle.objectif
    
class Defi(models.Model):
    
    libelle = models.ForeignKey(Libelle_Defi)
    enjeu_perso = models.CharField(max_length = 500, default = "Sans Enjeu")
    
    prive = models.BooleanField(default = False)
    
    ETAT = (
        ('D', 'Default'),
        ('E', 'Envoyé'),
        ('A', 'Accepté'),
        ('EX', 'Expiré'),
        ('R', 'Refusé'),
        ('AV', 'Attente de Validation'),
        ('V', 'Validé'),
        ('C', 'Contesté'),
        ('S', 'Signalé'),
    )
    
    etat = models.CharField(max_length=2, choices=ETAT, default='D')
    date_envoie = models.DateTimeField(auto_now=False, default = now)
    date_acceptation = models.DateTimeField(null = True)
    date_execution = models.DateTimeField(null = True)
    date_validation = models.DateTimeField(null = True)
    
    expire = models.BooleanField(default = False)
    
    contestation = models.ForeignKey(Contestation, null = True)
    signalement = models.ForeignKey(Signalement, null = True)
    preuve = models.ManyToManyField(Preuve)
    
    defieur = models.ForeignKey('Utilisateur' ,related_name="defieurdefi")
    challengeur = models.ForeignKey('Utilisateur' ,related_name="challengeurdefi")
    
    warning_triche = models.BooleanField(default = False)
    warning_analyse = models.BooleanField(default = False)
    
    def __str__(self):
        return self.libelle.nom
    
class Actualite (models.Model):
    
    date = models.DateTimeField(auto_now=False, default = now)
    message = models.CharField(max_length=555, default="Sans Message")
    nom = models.CharField(max_length=255, default="Sans Nom")
    personne_concernee = models.ForeignKey('Utilisateur')
    lien = models.CharField(max_length=555, default="Sans lien")
    
    def __str__(self):
        return self.nom
    
class MAJ (models.Model):
    
    date = models.DateTimeField(auto_now=False, default = now)
    
