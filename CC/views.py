# -*- coding: utf-8 -*-
from django.contrib.auth.models import User, UserManager, AnonymousUser
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponse
from django.template import RequestContext
import random, string
from datetime import datetime as dt, timedelta
from datetime import timezone
import pytz
from django.core import serializers
from django.contrib.staticfiles.templatetags.staticfiles import static
import smtplib
from CC.forms import *
from CC.models import *
from django.template import Context
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage
from email.mime.image import MIMEImage
from operator import itemgetter, attrgetter, methodcaller
from whitenoise.static_file import StaticFile
from django.http import JsonResponse
from io import StringIO, BytesIO
from PIL import Image
from resizeimage import resizeimage

def mise_a_jour (request):
    
    maintenant = datetime.now()
    delta = timedelta (minutes = 3)
    test = maintenant - delta
    maj = MAJ.objects.filter(date__gte = test)
   
    if not maj :
        
        arene_defi_expiration(request)
        maj_new = MAJ(date = maintenant)
        maj_new.save()
        
    return

def message_alerte (request):
    
    try :
        message = request.session['message']
        type_message = request.session['type_message']
        del request.session['message']
        del request.session['type_message']
        
    except :
        message = "False"
        type_message = "alert-success"
    
    return message, type_message
    
def import_image (request):
    
    message , type_message = message_alerte(request)
    
    if request.method == 'POST': 
        form = Formulaire_Import_Image(request.POST, request.FILES)
        if form.is_valid():
            
            nom = form.cleaned_data['nom'] 
            
            image_field = form.cleaned_data['image']
            image_file = BytesIO(image_field.read())
            image = Image.open(image_file)
            
            TAILLE = [400, 400]
            
            image = resizeimage.resize_cover(image, TAILLE)
            
            image_file = BytesIO()
            image.save(image_file, 'JPEG', quality=90)
            
            image_field.file = image_file
            
            pp = Photo(image=image_field,  nom=nom)
            pp.save()
            TAILLE = [100, 100]
            
            image = resizeimage.resize_cover(image, TAILLE)
            
            image_file = BytesIO()
            image.save(image_file, 'JPEG', quality=90)
            
            image_field.file = image_file
            
            pp.thumbnail = image_field
            pp.save()
            
            request.session['message'] = "L'image a bien été importée! " 
            
            redirect(home)
    else :
        form = Formulaire_Import_Image()
    return render(request, 'CC/user/compte/admin/pp.html', locals()) 

def home (request):
    
    if request.user.id :
        identifiant_utilisateur = request.user.id
        return redirect(user_dashboard)

    message, type_message = message_alerte(request)
    form = Formulaire_Inscription                   
    
    return render(request, 'CC/index.html', locals()) 


def inscription (request):
    
    lien_source = False
    message, type_message = message_alerte(request)

    try:
        lien_source = request.session['lien']
        del request.session['lien']
    except KeyError :
        pass
    
    if request.method == 'POST':  
        form = Formulaire_Inscription(request.POST)  

        if form.is_valid(): 
            
            username = form.cleaned_data['username'].lower()
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            first_name = form.cleaned_data['first_name'].lower()
            last_name = form.cleaned_data['last_name'].lower()
            
            user = Utilisateur.objects.create_user(username, email, password)
            user.first_name = first_name
            user.last_name = last_name
            user.nom_entier = first_name + ' ' + last_name
            
            user.save()
            
            email_inscription(request, user)
            request.session['messages'] = "Vous êtes bien inscrit."
            
            user = authenticate(username=username, password=password) 
            if user:  
                login(request, user)  
            
            if lien_source != False :
                return redirect("/" + lien_source)
            else :
                return redirect('home')

    else: 
        form = Formulaire_Inscription()  
    

    return render(request, 'CC/inscription.html', locals())


def connexion (request):
        
    error = False
    lien_source = False
    message, type_message = message_alerte(request)

    try:
        lien_source = request.session['lien']
        del request.session['lien']
    except KeyError :
        pass
    
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(username=username, password=password)
        
        if user:  
            login(request, user)
            
            if lien_source != False and lien_source != "connexion":
                return redirect("/" + lien_source)
            
            else:
                return redirect(home)
                        
        else:
            error = True
    
    else :
        
        return render(request, 'CC/connexion.html', locals())
            

    return render(request, 'CC/connexion.html', locals())


def deconnexion (request):
    logout(request)
    
    return redirect(connexion)

def user_notification_page(request):
    
    identifiant_utilisateur = request.user.id
    utilisateur = Utilisateur.objects.get(id=identifiant_utilisateur)
    notifications, notifications_actives, notifications_new = user_notification(identifiant_utilisateur)
    message, type_message = message_alerte(request)
    
    notification = Notification.objects.filter(recepteur=utilisateur.id).order_by('-date')

    return render(request, 'CC/user/compte/notifications.html', locals())

def user_notification(id_user):
    
    identifiant_utilisateur = id_user
    utilisateur = Utilisateur.objects.get(id=identifiant_utilisateur)
    
    notifications = Notification.objects.filter(recepteur=utilisateur.id).order_by('-date')[:5]
    notifications_active = Notification.objects.filter(recepteur=utilisateur.id, active=True).order_by('-date')
    notifications_new = Notification.objects.filter(recepteur=utilisateur.id, vue=False).order_by('-date')
    
    return (notifications, notifications_active, notifications_new)

def user_notification_vue(request):
    
    identifiant_utilisateur = request.user.id
    utilisateur = Utilisateur.objects.get(id=identifiant_utilisateur)
    
    notifications = Notification.objects.filter(recepteur=utilisateur.id, vue=False)
    
    for notification in notifications :
        
        notification.vue = True
        notification.save()
    
    return

def user_notification_active(request, notif_id):
    
    identifiant_utilisateur = request.user.id
    utilisateur = Utilisateur.objects.get(id=identifiant_utilisateur)
    
    notif_id = request.GET['notif_id']
    
    notification = Notification.objects.get(id = notif_id, recepteur = utilisateur.id)
    notification.active = False
    notification.save()
    
    return 

@login_required(login_url='connexion')
def user_dashboard (request):
    
    mise_a_jour(request)
    identifiant_utilisateur = request.user.id
    utilisateur = Utilisateur.objects.get(id=identifiant_utilisateur)
    notifications, notifications_actives, notifications_new = user_notification(identifiant_utilisateur)
    
    if utilisateur.email_valide == False :
        request.session['message'] = "Vous n'avez pas valider votre adresse mail! Regardez dans vos mails!"
        request.session['type_message'] = "alert-danger"
    
    message, type_message = message_alerte(request)
    
    nom_page = "Le Vestiaire"
    
    nb_defis_gagnes = len(Defi.objects.filter(challengeur = utilisateur, etat = "V"))
    nb_defis_perdus = len(Defi.objects.filter(challengeur = utilisateur, etat = "C"))
    nb_defis_releves = nb_defis_gagnes + nb_defis_perdus
    
    defis_lances = Defi.objects.filter(defieur = utilisateur).order_by('-date_envoie')[:3]
    defis_recus = Defi.objects.filter(challengeur = utilisateur).order_by('-date_envoie')[:3]
    
    queryset = Utilisateur.objects.all().order_by('-score_absolu')
    utilisateurs = list(queryset)
    rang_absolu = utilisateurs.index(utilisateur) + 1
    actu = []
    
    for ami in utilisateur.amis.all() :
        try :
            maintenant = datetime.now()
            septjours = timedelta(days = 7)
            baseD = maintenant - septjours
            
            actus = Actualite.objects.filter(personne_concernee = ami, date__gte = baseD)
            if actus :
                for actualite in actus :
                    actu.append(actualite)
                                
        except :
            pass
          

    actus = sorted(actu, key=attrgetter('date'), reverse=True)[:20]
    
    return render(request, 'CC/user/compte/dashboard.html', locals())

def user_changement_pp (request):
    
    mise_a_jour(request)
    identifiant_utilisateur = request.user.id
    utilisateur = Utilisateur.objects.get(id=identifiant_utilisateur)
    notifications, notifications_actives, notifications_new = user_notification(identifiant_utilisateur)
    message, type_message = message_alerte(request)
    
    nom_page = "Le Vestiaire"
    
    message , type_message = message_alerte(request)
    
    if request.method == 'POST': 
        
        form = Formulaire_Import_Image(request.POST, request.FILES)
        if form.is_valid():
        
            nom = "photodeprofil"+str(utilisateur.username)
            
            image_field = form.cleaned_data['image']
            image_file = BytesIO(image_field.read())
            image = Image.open(image_file)
            
            TAILLE = [400, 400]
            
            image = resizeimage.resize_cover(image, TAILLE)
            
            image_file = BytesIO()
            image.save(image_file, 'JPEG', quality=90)
            
            image_field.file = image_file
            
            pp = Photo(image=image_field,  nom=nom)
            pp.save()
            TAILLE = [100, 100]
            
            image = resizeimage.resize_cover(image, TAILLE)
            
            image_file = BytesIO()
            image.save(image_file, 'JPEG', quality=90)
            
            image_field.file = image_file
            
            pp.thumbnail = image_field
            pp.save()
            
            request.session['message'] = "Vous avez bien changé de photo de profil"
            request.session['type_message'] = "alert-success"
            
            utilisateur.pp = pp
            utilisateur.save()
            
            return redirect(user_dashboard)
    
    else :
        form = Formulaire_Import_Image(request.POST, request.FILES)
    
    return render(request, 'CC/user/compte/changement_pp.html', locals()) 

def user_changement_pa (request):
    
    mise_a_jour(request)
    identifiant_utilisateur = request.user.id
    utilisateur = Utilisateur.objects.get(id=identifiant_utilisateur)
    notifications, notifications_actives, notifications_new = user_notification(identifiant_utilisateur)
    message, type_message = message_alerte(request)
    
    nom_page = "Le Vestiaire"
    
    message , type_message = message_alerte(request)
    
    if request.method == 'POST': 
        
        form = Formulaire_Import_Image(request.POST, request.FILES)
        if form.is_valid():
        
            nom = "photodeprofil"+str(utilisateur.username)
            
            image_field = form.cleaned_data['image']
            image_file = BytesIO(image_field.read())
            image = Image.open(image_file)
            
            TAILLE = [700, 400]
            
            image = resizeimage.resize_cover(image, TAILLE)
            
            image_file = BytesIO()
            image.save(image_file, 'JPEG', quality=90)
            
            image_field.file = image_file
            
            pa = Photo(image=image_field,  nom=nom)
            pa.save()
            TAILLE = [70, 40]
            
            image = resizeimage.resize_cover(image, TAILLE)
            
            image_file = BytesIO()
            image.save(image_file, 'JPEG', quality=90)
            
            image_field.file = image_file
            
            pa.thumbnail = image_field
            pa.save()
            
            request.session['message'] = "Vous avez bien changé de photo d'accueil"
            request.session['type_message'] = "alert-success"
            
            utilisateur.pa = pa
            utilisateur.save()
            
            return redirect(user_dashboard)
    
    else :
        form = Formulaire_Import_Image(request.POST, request.FILES)
    
    return render(request, 'CC/user/compte/changement_pa.html', locals())

@login_required(login_url='connexion')
def user_changement_mdp (request):
    
    identifiant_utilisateur = request.user.id
    utilisateur = Utilisateur.objects.get(id=identifiant_utilisateur)
    notifications, notifications_actives, notifications_new = user_notification(identifiant_utilisateur)
    message, type_message = message_alerte(request)
    
    if request.method == 'POST':
        form = Formulaire_Change_MDP(request.POST)
        if form.is_valid():
            password1 = form.cleaned_data['password']
            password2 = form.cleaned_data['password2']
            
            if password1 != password2 :
                request.session['message'] = "Les mots de passe saisie sont incorrects."
                request.session['type_message'] = "alert-danger"
                return redirect(user_changement_mdp)
            
            else :
                utilisateur.set_password(password1)
                utilisateur.save()
                
                user = authenticate(username=utilisateur.username, password=password1)
        
                if user:  
                    login(request, user)
                
                    request.session['message'] = "Votre nouveau mot de passe a bien été enregistré."
                    request.session['type_message'] = "alert-success"
                    return redirect(user_profil_prive)
    
    else :
        form = Formulaire_Change_MDP()
     
  
    return render(request, 'CC/user/compte/changement_mdp.html', locals())

@login_required(login_url='connexion')
def user_map (request):
    
    identifiant_utilisateur = request.user.id
    utilisateur = Utilisateur.objects.get(id=identifiant_utilisateur)
    notifications, notifications_actives, notifications_new = user_notification(identifiant_utilisateur)
    message, type_message = message_alerte(request)
    nom_page = "La Map"
    
    users = utilisateur.amis.all().exclude(position = False)
    
    return render(request, 'CC/user/compte/map.html', locals())

@login_required(login_url='connexion')
def user_map_error (request):
    
    identifiant_utilisateur = request.user.id
    utilisateur = Utilisateur.objects.get(id=identifiant_utilisateur)
    notifications, notifications_actives, notifications_new = user_notification(identifiant_utilisateur)
    message, type_message = message_alerte(request)
    nom_page = "La Map"
    
    return render(request, 'CC/user/compte/map_error.html', locals())


def user_map_position (request, id_user, latitude, longitude):
    
    id_user = request.GET['id_user']
    utilisateur = Utilisateur.objects.get(id = id_user)
    date = datetime.now()
    
    try:
        latitude = request.GET['latitude']
        longitude = request.GET['longitude']
        
    except : 
        latitude = "0"
        longitude = "0"
        pass
    
    utilisateur.latitude = latitude
    utilisateur.longitude = longitude
    utilisateur.derniere_connexion = date
    utilisateur.position = True
    utilisateur.save()
    
    return


def user_map_track_user(request, id_user):
    
    id_user = request.GET['id_user']
    user = Utilisateur.objects.get(id = id_user)
    
    return JsonResponse({"geometry": { "type": "Point", "coordinates": [user.longitude , user.latitude]}, "type": "Feature", "properties": {"description": "<p><strong>"+user.first_name+" "+user.last_name+"</strong></br><a href='/compte/profil_public/?profil="+str(user.id)+"'>Voir Profil</a> </br> <a href='/arene/defi_user_cible/?id_user="+str(user.id)+"'>Défier</a></p>",}})


def user_map_track_me(request, id_user):
    
    id_user = request.GET['id_user']
    user = Utilisateur.objects.get(id = id_user)
    
    return JsonResponse({"geometry": { "type": "Point", "coordinates": [user.longitude , user.latitude]}, "type": "Feature", "properties": {"description": "<p><strong>Moi</strong></br><a href='/compte/profil_public/?profil="+str(user.id)+"'>Voir Profil</a></p>",}})


@login_required(login_url='connexion') 
def user_amis(request):
    
    identifiant_utilisateur = request.user.id
    utilisateur = Utilisateur.objects.get(id=identifiant_utilisateur)
    notifications, notifications_actives, notifications_new = user_notification(identifiant_utilisateur)
    message, type_message = message_alerte(request)
    nom_page = "Mes Challengeurs"
    
    amis = utilisateur.amis.all()
    nb_demandes = DemandeAmi.objects.filter(recepteur= utilisateur, active = True).count
    
    return render(request, 'CC/user/compte/mes_amis.html', locals())

@login_required(login_url='connexion') 
def user_defis(request):
    
    identifiant_utilisateur = request.user.id
    utilisateur = Utilisateur.objects.get(id=identifiant_utilisateur)
    notifications, notifications_actives, notifications_new = user_notification(identifiant_utilisateur)
    message, type_message = message_alerte(request)
    nom_page = "Mes Défis"
    
    defis_lances = Defi.objects.filter(defieur = utilisateur).order_by('-date_envoie')
    defis_recus = Defi.objects.filter(challengeur = utilisateur).order_by('-date_envoie')
    
    return render(request, 'CC/user/compte/mes_defis.html', locals())

@login_required(login_url='connexion') 
def user_demande_ami_page(request):
    
    identifiant_utilisateur = request.user.id
    utilisateur = Utilisateur.objects.get(id=identifiant_utilisateur)
    notifications, notifications_actives, notifications_new = user_notification(identifiant_utilisateur)
    message, type_message = message_alerte(request)
    
    rien = False
    demandes_recues = DemandeAmi.objects.filter(recepteur= utilisateur, active = True)
    
    if not demandes_recues : 
        rien = True
    return render(request, 'CC/user/compte/demande_ami.html', locals())

@login_required(login_url='connexion') 
def user_demande_defi_page(request):
    
    identifiant_utilisateur = request.user.id
    utilisateur = Utilisateur.objects.get(id=identifiant_utilisateur)
    notifications, notifications_actives, notifications_new = user_notification(identifiant_utilisateur)
    message, type_message = message_alerte(request)
    
    defis = Defi.objects.filter(type="D", recepteur = utilisateur)
    
    return render(request, 'CC/user/compte/demande_defi_page.html', locals())

@login_required(login_url='connexion')
def user_demande_ami(request, id_ami):
    
    identifiant_utilisateur = request.user.id
    utilisateur = Utilisateur.objects.get(id=identifiant_utilisateur)
    notifications, notifications_actives, notifications_new = user_notification(identifiant_utilisateur)
    message, type_message = message_alerte(request)
    
    x = request.GET['id_ami']
    ami = Utilisateur.objects.get(id=x)
    
    demande = DemandeAmi(auteur = utilisateur, recepteur = ami, active = True)
    demande.save()
    
    message = str (utilisateur.username.title()) + " vous a demandé en ami."
    lien = '/compte/demande_ami/page'
    
    notification = Notification(type="DA", message=message, lien=lien, auteur=utilisateur, recepteur=ami)
    notification.save()
    
    request.session['messages'] = "Votre demande a bien été envoyé à " + ami.username + "!"
    
    return redirect('/compte/profil_public/?profil=' + x)


@login_required(login_url='connexion') 
def user_ajout_ami(request, id_ami):
    
    identifiant_utilisateur = request.user.id
    utilisateur = Utilisateur.objects.get(id=identifiant_utilisateur)
    notifications, notifications_actives, notifications_new = user_notification(identifiant_utilisateur)
    message, type_message = message_alerte(request)
    
    x = request.GET['id_ami']    
    ami = Utilisateur.objects.get(id=x)
    
    message = str (utilisateur.username.title()) + " a accepté votre demande d'amitié."
    lien = '/compte/profil_public/?profil=' + str(utilisateur.id)
    
    
    notification = Notification(type="DA", message=message, lien=lien, auteur=utilisateur, recepteur=ami)
    notification.save()
    
    ami.amis.add(utilisateur)
    utilisateur.amis.add(ami)
    utilisateur.save()
    
    demande = DemandeAmi.objects.get(auteur = ami, recepteur = utilisateur, active = True)
    demande.active = False
    demande.save()
    
    request.GET = {'profil' : x}
    
    return redirect('/compte/profil_public/?profil=' + x)


@login_required(login_url='connexion') 
def user_refu_ami(request, id_ami):
    
    identifiant_utilisateur = request.user.id
    utilisateur = Utilisateur.objects.get(id=identifiant_utilisateur)
    notifications, notifications_actives, notifications_new = user_notification(identifiant_utilisateur)
    message, type_message = message_alerte(request)
    
    x = request.GET['id_ami']    
    ami = Utilisateur.objects.get(id=x)
    
    message = str (utilisateur.username.title()) + " a décliné votre demande d'amitié."
    lien = '/compte/profil_public/?profil=' + x
    notification = Notification(type="DA", message=message, lien=lien, auteur=utilisateur, recepteur=ami)
    notification.save()

    demande = DemandeAmi.objects.get(auteur = ami, recepteur = utilisateur, active = True)
    demande.active = False
    demande.save()
    
    return redirect(user_dashboard)

@login_required(login_url='connexion')
def user_profil_prive (request):
    
    identifiant_utilisateur = request.user.id
    utilisateur = Utilisateur.objects.get(id=identifiant_utilisateur)
    notifications, notifications_actives, notifications_new = user_notification(identifiant_utilisateur)
    message, type_message = message_alerte(request)
    
    nom_page = "Le Vestiaire"
     
    type = "moi"
    
    user_profil = utilisateur
    queryset = Utilisateur.objects.all().order_by('-score_absolu')
    utilisateurs = list(queryset)
    rang_absolu = utilisateurs.index(user_profil) + 1
    
    nb_defis_releves = len(Defi.objects.filter(challengeur = utilisateur, etat = "V"))
    nb_defis_lances = len(Defi.objects.filter(defieur = utilisateur))
    actus = Actualite.objects.filter(personne_concernee = utilisateur).order_by('-date')[:25]
    nbr_defis_proposes = len(Proposition_Defi.objects.filter(auteur = utilisateur))

    if user_profil.pp :
        pp = user_profil.pp
    else :
        ppinter = Photo.objects.get(nom="ppdefault")
        pp = ppinter.image
    
    return render(request, 'CC/user/user.html', locals())

@login_required(login_url='connexion')
def user_profil_public (request, profil):
    
    identifiant_utilisateur = request.user.id
    utilisateur = Utilisateur.objects.get(id=identifiant_utilisateur)
    notifications, notifications_actives, notifications_new = user_notification(identifiant_utilisateur)
    message, type_message = message_alerte(request)
    
    nom_page = "Mes Challengeurs"
    
    
    type = "pas_ami"
    profil = request.GET['profil']
    user_profil = Utilisateur.objects.get(id=profil)
    
    queryset = Utilisateur.objects.all().order_by('-score_absolu')
    utilisateurs = list(queryset)
    rang_absolu = utilisateurs.index(user_profil) + 1
    
    nb_defis_releves = len(Defi.objects.filter(challengeur = user_profil, etat = "V"))
    nb_defis_lances = len(Defi.objects.filter(defieur = user_profil))
    demande = False
    
    try :
        demande = DemandeAmi.objects.filter(recepteur = utilisateur, auteur = user_profil, active = True)     
    except :
        pass
    
    if demande :
        type = "attente"
    
    notification_demande_ami = Notification.objects.filter(type="DA", recepteur = user_profil, auteur = utilisateur)
        
    if notification_demande_ami :
        type = "demande_ami"
     
    if user_profil in utilisateur.amis.all() :
        type = "ami"
        
    if user_profil == utilisateur :
        return redirect(user_profil_prive)
    
    if user_profil.pp :
        pp = user_profil.pp
    else :
        ppinter = Photo.objects.get(nom="ppdefault")
        pp = ppinter.image
        
    actus = Actualite.objects.filter(personne_concernee = user_profil).order_by('-date')[:25]

    return render(request, 'CC/user/user.html', locals())

@login_required(login_url='connexion')
def user_proposition_defi (request):
    
    identifiant_utilisateur = request.user.id
    utilisateur = Utilisateur.objects.get(id=identifiant_utilisateur)
    notifications, notifications_actives, notifications_new = user_notification(identifiant_utilisateur)
    message, type_message = message_alerte(request)
    
    nom_page = "Le Vestiaire"

    if request.method == 'POST':
        
        nom = request.POST['nom']
        description = request.POST['description']
        
        defi = Proposition_Defi(nom=nom, description=description, auteur=utilisateur)
        defi.save()
        
        request.session['message'] = "Merci pour votre proposition, nous allons la traiter dans les plus bref delais"
        request.session['type_message'] = "alert-success"
        
        return redirect(user_proposition_defi)
    
    return render(request, 'CC/user/compte/proposition_defi.html', locals())


@login_required(login_url='connexion')
def user_proposition_defi_etat (request):
    
    identifiant_utilisateur = request.user.id
    utilisateur = Utilisateur.objects.get(id=identifiant_utilisateur)
    notifications, notifications_actives, notifications_new = user_notification(identifiant_utilisateur)
    message, type_message = message_alerte(request)
    
    nom_page = "Le Vestiaire"

    defis = Proposition_Defi.objects.filter(auteur = utilisateur)

    return render(request, 'CC/user/compte/proposition_etat.html', locals())


@login_required(login_url='connexion')
def user_classement (request):
    
    identifiant_utilisateur = request.user.id
    utilisateur = Utilisateur.objects.get(id=identifiant_utilisateur)
    notifications, notifications_actives, notifications_new = user_notification(identifiant_utilisateur)
    message, type_message = message_alerte(request)
    
    themes = Theme.objects.all()
    nom_page = "Les Classements"
    
    classement_absolu = Utilisateur.objects.all().order_by('-score_absolu')
    utilisateurs = list(classement_absolu)
    rang_absolu = utilisateurs.index(utilisateur) + 1
    
    classement_sport = Utilisateur.objects.all().order_by('-score_sport')
    utilisateurs = list(classement_sport)
    rang_sport = utilisateurs.index(utilisateur) + 1
    
    classement_cuisine = Utilisateur.objects.all().order_by('-score_cuisine')
    utilisateurs = list(classement_cuisine)
    rang_cuisine = utilisateurs.index(utilisateur) + 1
    
    classement_extreme = Utilisateur.objects.all().order_by('-score_extreme')
    utilisateurs = list(classement_extreme)
    rang_extreme = utilisateurs.index(utilisateur) + 1
    
    classement_arts = Utilisateur.objects.all().order_by('-score_arts')
    utilisateurs = list(classement_arts)
    rang_arts = utilisateurs.index(utilisateur) + 1
    
    classement_social_environnement = Utilisateur.objects.all().order_by('-score_social_environnement')
    utilisateurs = list(classement_social_environnement)
    rang_social_environnement = utilisateurs.index(utilisateur) + 1
    
    classement_autre = Utilisateur.objects.all().order_by('-score_autre')
    utilisateurs = list(classement_autre)
    rang_autre = utilisateurs.index(utilisateur) + 1
    
    return render(request, 'CC/user/compte/classements.html', locals())

def user_validation_email(request, id_user):
    
    id_user = request.GET['id_user']
    utilisateur = Utilisateur.objects.get(id = id_user)
    utilisateur.email_valide = True
    utilisateur.save()
    
    return redirect(user_dashboard)

@login_required(login_url='connexion')
def recherche (request):
    
    identifiant_utilisateur = request.user.id
    utilisateur = Utilisateur.objects.get(id=identifiant_utilisateur)
    notifications, notifications_actives, notifications_new = user_notification(identifiant_utilisateur)
    message, type_message = message_alerte(request)
    
    data_ami = []
    amis_pseudo = []
    amis_nom = []
    amis_prenom = []
    amis_full_name = []

    
    if request.method == 'POST':
        raw_data = request.POST['data'].lower()
       
        try : 
            amis_pseudo = Utilisateur.objects.filter(username=raw_data)
        except :  
            pass
        try : 
            amis_nom = Utilisateur.objects.filter(last_name=raw_data)
        except :  
            pass
        try : 
            amis_prenom = Utilisateur.objects.filter(first_name=raw_data)
        except :  
            pass
        try : 
            amis_full_name = Utilisateur.objects.filter(full_name=raw_data)
        except :  
            pass
       
        for ami in amis_pseudo :
            if not ami in data_ami and ami != utilisateur :
                data_ami.append(ami) 

        for ami in amis_nom :
            if not ami in data_ami and ami != utilisateur:
                data_ami.append(ami)
                                    
        for ami in amis_prenom :
            if not ami in data_ami and ami != utilisateur:
                data_ami.append(ami)
                    
        for ami in amis_full_name :
            if not ami in data_ami and ami != utilisateur :
                data_ami.append(ami)
                
    return render(request, 'CC/recherche.html', locals())

def arene_defi_cible(request, id_user):
    
    id_user = request.GET['id_user']
    request.session['user']=id_user
    
    return redirect(arene_accueil)

@login_required(login_url='connexion')
def arene_accueil (request):
    
    identifiant_utilisateur = request.user.id
    utilisateur = Utilisateur.objects.get(id=identifiant_utilisateur)
    notifications, notifications_actives, notifications_new = user_notification(identifiant_utilisateur)
    message, type_message = message_alerte(request)
    nom_page = "L'Arene"

    try :
        id_user = request.session['user']
        cible = Utilisateur.objects.get(id = id_user)
    except :
        pass
    
    categories = Theme.objects.all()
    sous_categories = Sous_Theme.objects.all()
    libelles = Libelle_Defi.objects.all()
    
    return render(request, 'CC/arene/accueil.html', locals())

@login_required(login_url='connexion')
def arene_accueil_defi (request, id_defi):
    
    identifiant_utilisateur = request.user.id
    utilisateur = Utilisateur.objects.get(id=identifiant_utilisateur)
    notifications, notifications_actives, notifications_new = user_notification(identifiant_utilisateur)
    message, type_message = message_alerte(request)
    nom_page = "L'Arene"
    
    cible = ""
    
    try :
        id_user = request.session['user']
        cible = Utilisateur.objects.get(id = id_user)
        del request.session['user']
    except :
        pass
    
    id_defi = request.GET['id_defi']
    categories = Theme.objects.all()
    sous_categories = Sous_Theme.objects.all()
    libelle = Libelle_Defi.objects.get(id = id_defi)
    
    return render(request, 'CC/arene/defi_libelle.html', locals())


@login_required(login_url='connexion')
def arene_defi_page (request, id_defi):
    
    identifiant_utilisateur = request.user.id
    utilisateur = Utilisateur.objects.get(id=identifiant_utilisateur)
    notifications, notifications_actives, notifications_new = user_notification(identifiant_utilisateur)
    message, type_message = message_alerte(request)
    nom_page = "Mes Défis"

    defi_id = request.GET['id_defi']
    defi = Defi.objects.get(id=defi_id)
    
    photos = []
    videos = []
  
    if defi.date_execution :
        
        defi_date = defi.date_execution
        temp = timedelta(days = 7)
        date_butoire = defi_date+temp
        
        try :
            contestation = defi.contestation
        except : 
            pass
        
        for preuve in defi.preuve.all():
            
            ref_file= preuve.fichier.url
            extension=ref_file.split('.')[-1]
            
            if extension == "mp4" or extension == "MP4" :
                videos.append(preuve)
            else :
                photos.append(preuve)
           
        
    elif defi.date_acceptation :
        
        defi_date = defi.date_acceptation
        temp = timedelta(days = 7)
        date_butoire = defi_date+temp
        
        
    else :
        
        defi_date = defi.date_envoie
        temp = timedelta(days = 7)
        date_butoire = defi_date+temp
        
          
    if defi.challengeur == utilisateur or defi.defieur == utilisateur :
        pass
    else :
        request.session['messages']= "Vous n'avez pas le droit d'aller là!"
        return redirect(arene_accueil)
    
    return render(request, 'CC/arene/defi.html', locals())

@login_required(login_url='connexion')
def arene_defi_lance (request):
    
    identifiant_utilisateur = request.user.id
    utilisateur = Utilisateur.objects.get(id=identifiant_utilisateur)
    notifications, notifications_actives, notifications_new = user_notification(identifiant_utilisateur)
    message, type_message = message_alerte(request)
    

    libelle_defi_id = int(request.POST['defi'])
    defi = Libelle_Defi.objects.get(id=libelle_defi_id)
    
    
    try :
        challengeur_id = request.POST['ami']

    except :
        request.session['message'] = "Vous n'avez pas défini de Challengeur"
        request.session['type_message'] = "alert-danger"
        return redirect(arene_accueil)
    
    
    ami = Utilisateur.objects.get(id=challengeur_id)
    
    try : 
        maintenant = datetime.now()
        delta = timedelta(days = 7)
        date_voulue = maintenant - delta
        if Defi.objects.get(libelle = defi, challengeur = ami, defieur = utilisateur, date_envoie__gte = date_voulue) :
            request.session['message'] = "Vous avez déjà défié ce challengeur il y moins de 7 jours avec ce défi"
            request.session['type_message'] = "alert-danger"
            return redirect(arene_accueil)
    
    except:
        pass
       
    date = datetime.now()
    
    try :
        prive = request.POST['prive']
    except :
        prive = False
        pass
    
    try :
        enjeu = request.POST['enjeu']
        
    except :
        enjeu = "Sans enjeu"
        pass
    
    defi = Defi(libelle=defi, prive=prive, etat="E", defieur=utilisateur, enjeu_perso = enjeu, challengeur=ami, date_envoie = date)
    
    defi.save()
    
    message = "Vous avez été défié par " + utilisateur.username + " : " + defi.libelle.nom[:22] + "..."
    lien = "/arene/defi/?id_defi="+ str(defi.id)
    notification = Notification (type='D', message=message, recepteur=ami, auteur=utilisateur, lien = lien)
    
    request.session['message'] = "Votre défi a bien été envoyé à " + ami.username
    request.session['type_message'] = "alert-success"
    notification.save()
    
    return redirect(arene_accueil)

@login_required(login_url='connexion')
def arene_defi_accepte (request, id_defi):
    
    identifiant_utilisateur = request.user.id
    utilisateur = Utilisateur.objects.get(id=identifiant_utilisateur)
    notifications, notifications_actives, notifications_new = user_notification(identifiant_utilisateur)
    message, type_message = message_alerte(request)


    defi_id = request.GET['id_defi']
    defi = Defi.objects.get(id=defi_id)
    
    defi.etat = "A"
    defi.date_acceptation = datetime.now()
    defi.save()
    
    message = str(utilisateur.username) + " a accepté votre défi : " + defi.libelle.nom[:22]  + "..."
    lien = "/arene/defi/?id_defi="+ str(defi.id)
    notification = Notification (type='D', message=message, recepteur=defi.defieur, auteur=utilisateur, lien = lien, date = datetime.now())
    notification.save()
    
    return redirect('/arene/defi/?id_defi='+ str(defi.id))
    
@login_required(login_url='connexion')
def arene_defi_refuse (request, id_defi):
    
    identifiant_utilisateur = request.user.id
    utilisateur = Utilisateur.objects.get(id=identifiant_utilisateur)

    defi_id = request.GET['id_defi']
    defi = Defi.objects.get(id=defi_id)
    
    utilisateur.score_absolu = utilisateur.score_absolu - 5
    utilisateur.save()
    
    defi.etat = "R"
    defi.date_acceptation = datetime.now()
    defi.save()
    
    message = str(utilisateur.username) + " a décliné votre défi : " + defi.libelle.nom[:22]  + "..."
    notification = Notification (type='D', message=message, recepteur=defi.defieur, auteur=utilisateur, date = datetime.now())
    notification.save()  
    
    return redirect('/arene/defi/?id_defi='+ str(defi.id))

@login_required(login_url='connexion')
def arene_defi_preuve (request):
    
    identifiant_utilisateur = request.user.id
    utilisateur = Utilisateur.objects.get(id=identifiant_utilisateur)
    notifications, notifications_actives, notifications_new = user_notification(identifiant_utilisateur)
    message, type_message = message_alerte(request)

    if request.method == 'POST':  
        defi_id = request.POST['defi']
        defi = Defi.objects.get(id=defi_id)
        
        defi.etat = "AV"
        defi.date_execution = datetime.now()
        defi.save()
        files = request.FILES.getlist('preuves')
        nom_preuve = "DEFI"+str(defi.id)+"USER"+str(utilisateur.id)
        for f in files:
           preuve = Preuve(nom = nom_preuve, fichier = f)
           preuve.save()
           defi.preuve.add(preuve)
           defi.save()

           
    defi.save()
    
    lien = "/arene/defi/?id_defi="+ str(defi.id)
    message = str(utilisateur.username) + " a réalisé votre défi, venez le valider"
    notification = Notification (lien = lien, type='D', message=message, recepteur=defi.defieur, auteur=utilisateur, date = datetime.now())
    notification.save()  
    
    return redirect('/arene/defi/?id_defi='+ str(defi.id))


@login_required(login_url='connexion')
def arene_defi_valide (request, id_defi):
    
    identifiant_utilisateur = request.user.id
    utilisateur = Utilisateur.objects.get(id=identifiant_utilisateur)

    defi_id = request.GET['id_defi']
    defi = Defi.objects.get(id=defi_id)
    
    defi.challengeur.score_absolu = defi.challengeur.score_absolu + defi.libelle.recompense.points
    defi.challengeur.save()
    
    if defi.libelle.theme.nom == "Sport" :
        defi.challengeur.score_sport =  defi.challengeur.score_sport + defi.libelle.recompense.points
    if defi.libelle.theme.nom == "Cuisine" :
        defi.challengeur.score_cuisine =  defi.challengeur.score_cuisine + defi.libelle.recompense.points
    if defi.libelle.theme.nom == "Extreme" :
        defi.challengeur.score_extreme =  defi.challengeur.score_extreme + defi.libelle.recompense.points
    if defi.libelle.theme.nom == "Social/Environnement" :
        defi.challengeur.score_social_environnement =  defi.challengeur.score_social_environnement + defi.libelle.recompense.points
    if defi.libelle.theme.nom == "Arts" :
        defi.challengeur.score_arts =  defi.challengeur.score_arts + defi.libelle.recompense.points
    if defi.libelle.theme.nom == "Autre" :
        defi.challengeur.score_autre =  defi.challengeur.score_autre + defi.libelle.recompense.points
    
    defi.challengeur.save()
    
    defi.etat = "V"
    defi.date_validation = datetime.now()
    
    defi.save()
    
    lien = "/arene/defi/?id_defi="+ str(defi.id)
    message = str(utilisateur.username) + " a validé votre défi"
    notification = Notification (lien = lien, type='D', message=message, recepteur=defi.challengeur, auteur=utilisateur, date = datetime.now())
    notification.save()  
   
    if defi.prive == False :
        
        message = str (defi.challengeur.username +" a relevé le défi de "+ defi.defieur.username + " haut la main! Il devait : " +defi.libelle.nom)
        actu = Actualite(message = message, nom = "Defi", personne_concernee =  defi.challengeur)
        actu.save()
    
       
    if Quete.objects.filter(challengeur = defi.challengeur, active = True) :
        quete = Quete.objects.get(challengeur = defi.challengeur, active = True)
        quete_defis = quete.libelle.defis.all()
        
        les_defis_quete = []
        for libelle in quete_defis :
            les_defis_quete.append(libelle.id)
        
        if defi.libelle.id in les_defis_quete :
            date = quete.date_debut
            les_defis = Defi.objects.filter(challengeur = defi.challengeur, etat = "V", date_validation__gte = date)
        
            mes_success = []
            
            for defi in les_defis :
                mes_success.append(defi.libelle.id)
            
            for id in mes_success :
                try : 
                    les_defis_quete.remove(id)
                except :
                    pass
                
            if les_defis_quete == [] :
                quete_validation(request, quete.id)
                
            
    return redirect('/arene/defi/?id_defi='+ str(defi.id))

@login_required(login_url='connexion')
def arene_defi_conteste (request):
    
    identifiant_utilisateur = request.user.id
    utilisateur = Utilisateur.objects.get(id=identifiant_utilisateur)
    
    
    if request.method == 'POST':  
        defi_id = request.POST['defi']
        contenu = request.POST['motif']
        defi = Defi.objects.get(id=defi_id)
        
        defi.etat = "C"
        defi.save()
        
        nom_preuve = "CONTESTATIONDEFI"+str(defi.id)+"USER"+str(utilisateur.id)
        contestation = Contestation(nom = nom_preuve, contenu = contenu)
        contestation.save()
        
        defi.contestation = contestation
        defi.save()
        
        utilisateur.score_absolu = utilisateur.score_absolu + defi.recompense.points
        utilisateur.save()

    defi.save()
    
    lien = "/arene/defi/?id_defi="+ str(defi.id)
    message = str(utilisateur.username) + " a contesté votre défi, venez voir pourquoi."
    notification = Notification (lien = lien, type='D', message=message, recepteur=defi.challengeur, auteur=utilisateur, date = datetime.now())
    notification.save()  
    
    return redirect('/arene/defi/?id_defi='+ str(defi.id))

@login_required(login_url='connexion')
def arene_defi_signale (request):
    
    identifiant_utilisateur = request.user.id
    utilisateur = Utilisateur.objects.get(id=identifiant_utilisateur)

    if request.method == 'POST':  
        defi_id = request.POST['defi']
        defi = Defi.objects.get(id=defi_id)
        
        defi.etat = "S"
        defi.save()
        
        nom = "SIGNALERDEFI"+str(defi.id)+"USER"+str(utilisateur.id)
        motif = request.POST['motif']
        signalement = Signalement(nom = nom, motif = motif, defi = defi)
        
        signalement.save()
        

    defi.save()
    
    lien = "/arene/defi/?id_defi="+ str(defi.id)
    message = str(utilisateur.username) + " a signaler un abus de contestation votre défi."
    notification = Notification (lien = lien, type='D', message=message, recepteur=defi.challengeur, auteur=utilisateur, date = datetime.now())
    notification.save()  
    
    return redirect('/arene/defi/?id_defi='+ str(defi.id))

def arene_defi_expiration (request):

    maintenant = datetime.now()
    jour_verification = timedelta (days = -7)
    date_limite = maintenant + jour_verification
 
    
    #Test des défis envoyé
    defis = Defi.objects.filter(expire = False)
    defis_expiration = []
    
    for defi in defis :
        if defi.etat == "EX" :
            if defi.date_execution.replace(tzinfo=pytz.UTC) <= date_limite.replace(tzinfo=pytz.UTC) :
                defis_expiration.append(defi.id)
        elif defi.etat == "AV" :
            if defi.date_acceptation.replace(tzinfo=pytz.UTC) <= date_limite.replace(tzinfo=pytz.UTC) :
                defis_expiration.append(defi.id)
                
        elif defi.etat == "E" : 
            if defi.date_envoie.replace(tzinfo=pytz.UTC) <= date_limite.replace(tzinfo=pytz.UTC) :
                defis_expiration.append(defi.id)
            
    if defis_expiration is not [] :
        for defi in defis_expiration :
            arene_expiration_challengeur(request,defi)
    
    return

def arene_expiration_challengeur (request, id_defi):
    
    id_defi = id_defi
    
    defi = Defi.objects.get(id = id_defi)
    
    defi.etat = "EX"
    defi.expire = True
    defi.save()
    
    teamCC = Utilisateur.objects.get(username = "@teamcc")
    
    if defi.date_execution :
        defi.defieur.score_absolu = defi.defieur.score_absolu - defi.libelle.recompense.points
        
        lien = "/arene/defi/?id_defi="+ str(defi.id)
        message = "Vous n'avez pas validé le défis avec "+ str(defi.challengeur.username)+" dans les temps. Vous avez perdu "+ str(defi.libelle.recompense.points) 
        notification = Notification (lien = lien, type='D', message=message, recepteur=defi.defieur, auteur=teamCC, date = datetime.now())
        notification.save()
        
        
        lien = "/arene/defi/?id_defi="+ str(defi.id)
        message = "Malheuresemednt votre défi avec "+ str(defi.defieur.username)+" n'a pas été validé dans les temps par consequent le défieur perds les points engagés" 
        notification = Notification (lien = lien, type='D', message=message, recepteur=defi.challengeur, auteur=teamCC, date = datetime.now())
        notification.save() 
        
    return
    
def quete_accueil (request):
    
    identifiant_utilisateur = request.user.id
    utilisateur = Utilisateur.objects.get(id=identifiant_utilisateur)
    notifications, notifications_actives, notifications_new = user_notification(identifiant_utilisateur)
    message, type_message = message_alerte(request)
    nom_page = "Ma Quête"
    
    try :
        ma_quete = Quete.objects.filter(challengeur = utilisateur, active = True)
    except :
        pass
    
    if ma_quete : 
        return redirect(quete_ma_quete)
    
    libelles = Libelle_Quete.objects.all()
    categories = Theme.objects.all()
    
    return render(request, 'CC/quete/accueil.html', locals())

def quete_ma_quete (request):
    
    identifiant_utilisateur = request.user.id
    utilisateur = Utilisateur.objects.get(id=identifiant_utilisateur)
    notifications, notifications_actives, notifications_new = user_notification(identifiant_utilisateur)
    message, type_message = message_alerte(request)
    nom_page = "Ma Quête"
    
    quete = False
    
    try : 
        ma_quete = Quete.objects.get(challengeur = utilisateur, active = True)
        quete = True
    except :
        pass
    
    if quete == True :
        date = ma_quete.date_debut
        mes_defis = Defi.objects.filter(challengeur = utilisateur, etat = "V", date_validation__gte = date)
        mes_libelles = []
        
        try : 
            for defi in mes_defis :
                mes_libelles.append(defi.libelle.id)
                
        except : 
            mes_libelle = []
            pass
        
        mes_success = []
        for defi in ma_quete.libelle.defis.all() :
            if defi.id in mes_libelles :
                mes_success.append(defi.id)
        return render(request, 'CC/quete/ma_quete.html', locals())
    
    else : 
        return redirect(quete_accueil)
    
def quete_ma_quete_archive (request, id_quete):
    
    identifiant_utilisateur = request.user.id
    utilisateur = Utilisateur.objects.get(id=identifiant_utilisateur)
    notifications, notifications_actives, notifications_new = user_notification(identifiant_utilisateur)
    message, type_message = message_alerte(request)
    nom_page = "Ma Quête"
    
    id_quete = request.GET['id_quete']
    
    try :
        ma_quete = Quete.objects.get(id = id_quete, challengeur = utilisateur)
        
    except : 
        return redirect(quete_ma_quete)
   
    return render(request, 'CC/quete/ma_quete_archive.html', locals())
    

def quete_accepter_quete (request):
    
    identifiant_utilisateur = request.user.id
    utilisateur = Utilisateur.objects.get(id=identifiant_utilisateur)
    
    if request.method == 'POST': 
        test = False
        try :
            quete = Quete.objects.get(challengeur = utilisateur, active = True)
            test = True
        except :
            pass
        
        if test == True :
                request.session['message'] = "Vous avez déjà une quête en cours!"
                request.session['type_message'] = "alert-danger"
                return redirect(quete_ma_quete)
        
        id_quete = request.POST['id_quete']
        
        prive = False
        try :
            prive = request.POST['prive']
        except :
            pass
        
        libelle = Libelle_Quete.objects.get(id = id_quete)
        date_fin = datetime.now() + timedelta(days = libelle.duree)
        
        ma_quete = Quete(libelle = libelle, challengeur = utilisateur, prive = prive, etat = "D", date_fin = date_fin)
        ma_quete.save()
        
        if prive == False :
            message = str (utilisateur.username) +" s'est enrollé dans une quête épique : "+ str(ma_quete.libelle.objectif)
            lien = "/compte/profil_public/?profil="+str(utilisateur.id)
            actu = Actualite(message = message, nom = "Quête", personne_concernee = utilisateur, lien = lien)
            actu.save()
        return redirect(quete_ma_quete)
    
    return redirect(quete_accueil)

def quete_abandonner_quete (request):
    
    identifiant_utilisateur = request.user.id
    utilisateur = Utilisateur.objects.get(id=identifiant_utilisateur)
    test= False
    
    try : 
        quete = Quete.objects.get(challengeur = utilisateur, active = True)
        test = True
    except :
        pass
    
    if test == True :
        quete.active = False
        quete.save()
    
    return redirect(quete_accueil)

def quete_validation (request, id_quete):
    
    identifiant_utilisateur = request.user.id
    utilisateur = Utilisateur.objects.get(id=identifiant_utilisateur)
   
    quete = Quete.objects.get(id = id_quete, etat= "D")
    
    quete.etat = "V"
    quete.active = False
    quete.date_fin = datetime.now()
    
    lien = "/quete/ma_quete_archive/?id_quete="+ quete.id
    message = "Vous avez réussi votre quête!"
    team_CC = Utilisateur.objects.get(username = "@teamcc")
    notification = Notification (lien = lien, type='Q', message=message, recepteur=quete.challengeur, auteur=team_CC, date = datetime.now())
    notification.save()  
   
    if quete.prive == False :
        
        message = str (quete.challengeur.username) +" a fini sa quête : "+ str(quete.libelle.objectif)
        actu = Actualite(message = message, nom = "Quête", personne_concernee =  quete.challengeur)
        actu.save()
    
    quete.save()
    
    return

def quete_libelle_quete (request, id_quete):
    
    identifiant_utilisateur = request.user.id
    utilisateur = Utilisateur.objects.get(id=identifiant_utilisateur)
    notifications, notifications_actives, notifications_new = user_notification(identifiant_utilisateur)
    message, type_message = message_alerte(request)
    nom_page = "Ma Quête"
    
    id_quete = request.GET['id_quete']
    
    quete = Libelle_Quete.objects.get(id = id_quete)
    
    return render(request, 'CC/quete/quete.html', locals())

def admin_control_triche_ami (request):
    
    defis = Defi.objects.filter(warning_triche = False, warning_analyse = False, etat = "V")
    liste_warning = []
    
    temps_ecart_acceptable = timedelta(days = 1)
    
    for defi in defis :
        if (defi.date_execution - defi.date_validation) < temps_ecart_acceptable :
            defi.warning_triche = True
            defi.save()
        defi.warning_analyse = True
    
    
    return

def email_inscription (request, utilisateur):
    
    subject = "Challenges.Campo - Confirmation d'inscription"
    to = [utilisateur.email]
    from_email = 'noreply@challengescamp.com'

    image = Photo.objects.get(nom='Logo')
    
    image_mail = open(image.image.path, "rb")
    msg_img = MIMEImage(image_mail.read())
    msg_img.add_header('Content-ID', '<logo>')
    
    ctx = {
        'utilisateur': utilisateur,
    }

    message = get_template('CC/email/inscription.html').render(Context(ctx))
    msg = EmailMessage(subject, message, to=to, from_email=from_email)
    msg.content_subtype = 'html'
    msg.attach(msg_img)
    msg.send()
    
    
    return 