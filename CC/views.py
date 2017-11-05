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
from django.http import JsonResponse
from io import StringIO, BytesIO
from PIL import Image
from resizeimage import resizeimage
import csv
from django.db.models import Q
from django.core.serializers import serialize

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

@login_required(login_url='/connexion')
def user_dashboard (request):
    
    mise_a_jour(request)
    identifiant_utilisateur = request.user.id
    utilisateur = Utilisateur.objects.get(id=identifiant_utilisateur)
    notifications, notifications_actives, notifications_new = user_notification(identifiant_utilisateur)
    
    if utilisateur.email_valide == False :
        request.session['message'] = "Vous n'avez pas valider votre adresse mail! Regardez dans vos mails!"
        request.session['type_message'] = "alert-danger"
    
    message, type_message = message_alerte(request)
    
    test = len(MapPoint.objects.all())
    test2 = MapPoint.objects.filter(Q(y__gte = 2.24430)&Q(y__lte = 2.24318),Q(x__lte = 48.83425)&Q(x__gte = 48.83306))
    
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

@login_required(login_url='/connexion')
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


@login_required(login_url='/connexion')
def user_map (request):
    
    identifiant_utilisateur = request.user.id
    utilisateur = Utilisateur.objects.get(id=identifiant_utilisateur)
    notifications, notifications_actives, notifications_new = user_notification(identifiant_utilisateur)
    message, type_message = message_alerte(request)
    nom_page = "La Map"
    
    y = float(utilisateur.latitude)
    x = float(utilisateur.longitude)
    
    xmoins = x - 0.09
    ymoins = y - 0.07
    
    xplus = x + 0.09
    yplus = y + 0.07
    
    raws = MapPoint.objects.filter(Q(y__gte = ymoins)&Q(y__lte = yplus),Q(x__lte = xplus)&Q(x__gte = xmoins)).order_by('?').exclude(sous_categorie = "rien")[:670]
    nb_raws = len(raws)
    points_sport = []
    points_cuisine = []
    points_gaming = []
    points_citoyen = []
    points_creation = []
    points_elite = []
    points_autre = []

    for raw in raws :
        cat = raw.sous_categorie.split(";")
        sous_categorie = random.choice(cat)
        if sous_categorie == "rien" :
            Sous_Theme.objects.get(nom = "Autre")
        else :
            sous_categorie = Sous_Theme.objects.get(nom = sous_categorie)
            
        defi = Libelle_Defi.objects.filter(sous_theme = sous_categorie).order_by('?').exclude(active = False)[:1]
        point = MapPoint(x = raw.x, y = raw.y, categorie = raw.categorie, defi = defi[0])
        
        if sous_categorie.theme.nom == "Sport" :
            points_sport.append(point)
        elif sous_categorie.theme.nom == "Cuisine" :
            points_cuisine.append(point)
        elif sous_categorie.theme.nom == "Création" :
            points_creation.append(point)
        elif sous_categorie.theme.nom == "Citoyen" :
            points_citoyen.append(point)
        elif sous_categorie.theme.nom == "Gaming" :
            points_sport.append(point)
        elif sous_categorie.theme.nom == "Elite" :
            points_elite.append(point)
        elif sous_categorie.theme.nom == "Autre" :
            points_autre.append(point)
            
       
    if nb_raws < 700 :
        
        xmoins = x - 0.02
        ymoins = y - 0.009
        xplus = x + 0.02
        yplus = y + 0.009
        
        while (700 - nb_raws) > 1 :
            x = random.uniform(xmoins, xplus)
            y = random.uniform(ymoins, yplus)
            sous_categorie = Sous_Theme.objects.all().order_by('?')[:1]
            defi = Libelle_Defi.objects.filter(sous_theme = sous_categorie[0]).exclude(active = False).order_by('?')[:1]
            categorie = defi[0].theme.nom
            point = MapPoint(y = str(y), x = str(x) , categorie = categorie, defi = defi[0])
            
            if categorie == "Sport" :
                points_sport.append(point)
            elif categorie == "Cuisine" :
                points_cuisine.append(point)
            elif categorie == "Création" :
                points_creation.append(point)
            elif categorie == "Citoyen" :
                points_citoyen.append(point)
            elif categorie == "Gaming" :
                points_sport.append(point)
            elif categorie == "Elite" :
                points_elite.append(point)
            elif categorie == "Autre" :
                points_autre.append(point)

            nb_raws = nb_raws + 1
        
    icone_sport = Photo.objects.get(nom = "icone_sport")
    icone_cuisine = Photo.objects.get(nom = "icone_cuisine")
    icone_gaming = Photo.objects.get(nom = "icone_gaming")
    icone_autre = Photo.objects.get(nom = "icone_autre")
    icone_creation = Photo.objects.get(nom = "icone_creation")
    icone_elite = Photo.objects.get(nom = "icone_elite")
    icone_citoyen = Photo.objects.get(nom = "icone_citoyen")
    
    users = utilisateur.amis.all().exclude(position = False)
    
    return render(request, 'CC/user/compte/map.html', locals())


@login_required(login_url='/connexion')
def user_map_error (request):
    
    identifiant_utilisateur = request.user.id
    utilisateur = Utilisateur.objects.get(id=identifiant_utilisateur)
    notifications, notifications_actives, notifications_new = user_notification(identifiant_utilisateur)
    message, type_message = message_alerte(request)
    nom_page = "La Map"
    
    return render(request, 'CC/user/compte/map_error.html', locals())


def user_map_preload (request):
    identifiant_utilisateur = request.user.id
    utilisateur = Utilisateur.objects.get(id=identifiant_utilisateur)
    
    return render(request, 'CC/user/compte/map_preload.html', locals())


def user_map_track_user(request, id_user):
    
    id_user = request.GET['id_user']
    user = Utilisateur.objects.get(id = id_user)
    
    return JsonResponse({"geometry": { "type": "Point", "coordinates": [user.longitude , user.latitude]}, "type": "Feature", "properties": {"description": "<p><strong>"+user.first_name+" "+user.last_name+"</strong></br><a href='/compte/profil_public/?profil="+str(user.id)+"'>Voir Profil</a> </br> <a href='/arene/defi_user_cible/?id_user="+str(user.id)+"'>Défier</a></p>",}})


def user_map_track_me(request, id_user):
    
    id_user = request.GET['id_user']
    user = Utilisateur.objects.get(id = id_user)
    
    return JsonResponse({"geometry": { "type": "Point", "coordinates": [user.longitude , user.latitude]}, "type": "Feature", "properties": {"description": "<p><strong>Moi</strong></br><a href='/compte/profil_public/?profil="+str(user.id)+"'>Voir Profil</a></p>",}})

def user_map_push_position(request, id_user, latitude, longitude):
    
    id_user = request.GET['id_user']
    latitude = request.GET['latitude']
    longitude = request.GET['longitude']
    user = Utilisateur.objects.get(id = id_user)
    
    user.longitude = longitude
    user.latitude = latitude
    
    user.save()
    
    return HttpResponse("OK")

@login_required(login_url='/connexion') 
def user_map_tri(request):
    identifiant_utilisateur = request.user.id
    utilisateur = Utilisateur.objects.get(id=identifiant_utilisateur)
    notifications, notifications_actives, notifications_new = user_notification(identifiant_utilisateur)
    message, type_message = message_alerte(request)
    nom_page = "Map"
    
    points = MapPoint.objects.filter(attribut__contains = 'bicycle_rental')
    
    for point in points :
        point.categorie = "Sport"
        point.sous_categorie = "Vélo"
        point.save()
    
    return  render(request, 'CC/user/compte/map_tri.html', locals())

@login_required(login_url='/connexion')
def user_map_proposition_point (request):
    
    identifiant_utilisateur = request.user.id
    utilisateur = Utilisateur.objects.get(id=identifiant_utilisateur)
    notifications, notifications_actives, notifications_new = user_notification(identifiant_utilisateur)
    message, type_message = message_alerte(request)
    
    nom_page = "Le Vestiaire"
    
    latitude = utilisateur.latitude
    longitude = utilisateur.longitude

    if request.method == 'POST':
        
        nom = request.POST['nom']
        description = request.POST['description']
        
        point = Proposition_Point(nom=nom, description=description, auteur=utilisateur, latitude = latitude, longitude = longitude)
        point.save()
        
        request.session['message'] = "Merci pour votre proposition, nous allons la traiter dans les plus bref delais"
        request.session['type_message'] = "alert-success"
        
        return redirect(user_map_preload)
    
    return render(request, 'CC/user/compte/proposition_map_point.html', locals())

@login_required(login_url='/connexion') 
def user_amis(request):
    
    identifiant_utilisateur = request.user.id
    utilisateur = Utilisateur.objects.get(id=identifiant_utilisateur)
    notifications, notifications_actives, notifications_new = user_notification(identifiant_utilisateur)
    message, type_message = message_alerte(request)
    nom_page = "Mes Challengeurs"
    
    amis = utilisateur.amis.all()
    nb_demandes = DemandeAmi.objects.filter(recepteur= utilisateur, active = True).count
    
    return render(request, 'CC/user/compte/mes_amis.html', locals())

@login_required(login_url='/connexion') 
def user_defis(request):
    
    identifiant_utilisateur = request.user.id
    utilisateur = Utilisateur.objects.get(id=identifiant_utilisateur)
    notifications, notifications_actives, notifications_new = user_notification(identifiant_utilisateur)
    message, type_message = message_alerte(request)
    nom_page = "Mes Défis"
    
    defis_lances = Defi.objects.filter(defieur = utilisateur).order_by('-date_envoie')
    defis_recus = Defi.objects.filter(challengeur = utilisateur).order_by('-date_envoie')
    
    return render(request, 'CC/user/compte/mes_defis.html', locals())

@login_required(login_url='/connexion') 
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

@login_required(login_url='/connexion') 
def user_demande_defi_page(request):
    
    identifiant_utilisateur = request.user.id
    utilisateur = Utilisateur.objects.get(id=identifiant_utilisateur)
    notifications, notifications_actives, notifications_new = user_notification(identifiant_utilisateur)
    message, type_message = message_alerte(request)
    
    defis = Defi.objects.filter(type="D", recepteur = utilisateur)
    
    return render(request, 'CC/user/compte/demande_defi_page.html', locals())

@login_required(login_url='/connexion')
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


@login_required(login_url='/connexion') 
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


@login_required(login_url='/connexion') 
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

@login_required(login_url='/connexion')
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

@login_required(login_url='/connexion')
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

@login_required(login_url='/connexion')
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


@login_required(login_url='/connexion')
def user_proposition_etat (request):
    
    identifiant_utilisateur = request.user.id
    utilisateur = Utilisateur.objects.get(id=identifiant_utilisateur)
    notifications, notifications_actives, notifications_new = user_notification(identifiant_utilisateur)
    message, type_message = message_alerte(request)
    
    nom_page = "Le Vestiaire"

    defis = Proposition_Defi.objects.filter(auteur = utilisateur)
    points = Proposition_Point.objects.filter(auteur = utilisateur)

    return render(request, 'CC/user/compte/proposition_etat.html', locals())


@login_required(login_url='/connexion')
def user_classement (request):
    
    identifiant_utilisateur = request.user.id
    utilisateur = Utilisateur.objects.get(id=identifiant_utilisateur)
    notifications, notifications_actives, notifications_new = user_notification(identifiant_utilisateur)
    message, type_message = message_alerte(request)
    
    themes = Theme.objects.all()
    nom_page = "Les Classements"
    
    classements = {}
    
    
    absolu = Utilisateur.objects.all().order_by('-score_absolu')
    utilisateurs = list(absolu)
    rang_absolu = utilisateurs.index(utilisateur) + 1
    classements['absolu'] = absolu
    
    sport = Utilisateur.objects.all().order_by('-score_sport')
    utilisateurs = list(sport)
    rang_sport = utilisateurs.index(utilisateur) + 1
    classements['sport'] = sport
    
    cuisine = Utilisateur.objects.all().order_by('-score_cuisine')
    utilisateurs = list(cuisine)
    rang_cuisine = utilisateurs.index(utilisateur) + 1
    classements['cuisine'] = cuisine
    
    extreme = Utilisateur.objects.all().order_by('-score_elite')
    utilisateurs = list(extreme)
    rang_extreme = utilisateurs.index(utilisateur) + 1
    classements['elite'] = extreme
    
    arts = Utilisateur.objects.all().order_by('-score_gaming')
    utilisateurs = list(arts)
    rang_arts = utilisateurs.index(utilisateur) + 1
    classements['gaming'] = arts
    
    social_environnement = Utilisateur.objects.all().order_by('-score_citoyen')
    utilisateurs = list(social_environnement)
    rang_social_environnement = utilisateurs.index(utilisateur) + 1
    classements['citoyen'] = social_environnement
    
    autre = Utilisateur.objects.all().order_by('-score_autre')
    utilisateurs = list(autre)
    rang_autre = utilisateurs.index(utilisateur) + 1
    classements['autre'] = autre
    
    return render(request, 'CC/user/compte/classements.html', locals())

def user_validation_email(request, id_user):
    
    id_user = request.GET['id_user']
    utilisateur = Utilisateur.objects.get(id = id_user)
    utilisateur.email_valide = True
    utilisateur.save()
    
    return redirect(user_dashboard)

@login_required(login_url='/connexion')
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
    
    utilisateurs = Utilisateur.objects.all().exclude(id = utilisateur.id)
    
    if request.method == "POST":
        try :
            raw_data = str(request.POST['data'])
        except :
            pass
        
        if raw_data :
            raw_data = str(request.POST['data'])
        else :
            raw_data = str(request.POST['data_grand'])
       
       
                
    return render(request, 'CC/recherche.html', locals())

def arene_defi_cible(request, id_user):
    
    id_user = request.GET['id_user']
    request.session['user']=id_user
    
    return redirect(arene_accueil)

@login_required(login_url='/connexion')
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
    libelles = Libelle_Defi.objects.all().exclude(active = False)
    
    return render(request, 'CC/arene/accueil.html', locals())

@login_required(login_url='/connexion')
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


@login_required(login_url='/connexion')
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
    visiteur = False
    
    if defi.date_execution :
        
        defi_date = defi.date_execution
        temp = timedelta(days = 2)
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
        nb_mins = defi.libelle.duree_execution
        temp = timedelta(minutes = nb_mins)
        date_butoire = defi_date+temp
        
        
    else :
        
        defi_date = defi.date_envoie
        nb_mins = defi.libelle.duree_acceptation
        temp = timedelta(minutes = nb_mins)
        date_butoire = defi_date+temp
        
    
    if defi.prive == True :     
        if defi.challengeur == utilisateur or defi.defieur == utilisateur :
            pass
        else :
            request.session['message']= "Vous n'avez pas le droit d'aller là. Ceci est un défi privé!"
            request.session['type_message'] = "alert-warning"
            return redirect(arene_accueil)
    else :
        if defi.challengeur == utilisateur or defi.defieur == utilisateur :
            pass
        else :
            visiteur = True
        
    return render(request, 'CC/arene/defi.html', locals())

@login_required(login_url='/connexion')
def arene_defi_page_moderation (request):
    
    identifiant_utilisateur = request.user.id
    utilisateur = Utilisateur.objects.get(id=identifiant_utilisateur)
    notifications, notifications_actives, notifications_new = user_notification(identifiant_utilisateur)
    message, type_message = message_alerte(request)
    nom_page = "Arene"
    
    teamcc = Utilisateur.objects.get(username = "@teamcc")
    prive = False
    
    defi = Defi.objects.filter(defieur=teamcc, etat="AV", prive = prive).order_by('-date_execution').exclude(challengeur = utilisateur)[:1]
    
    if len(defi) == 0  :
        return redirect(arene_defi_page_moderation_vide)
    
    defi = defi[0]
    photos = []
    videos = []
    visiteur = False
        
    for preuve in defi.preuve.all():
        
        ref_file= preuve.fichier.url
        extension=ref_file.split('.')[-1]
        
        if extension == "mp4" or extension == "MP4" :
            videos.append(preuve)
        else :
            photos.append(preuve)
           
           
    return render(request, 'CC/arene/defi_moderation.html', locals())

@login_required(login_url='/connexion')
def arene_defi_page_moderation_vide (request):
    
    identifiant_utilisateur = request.user.id
    utilisateur = Utilisateur.objects.get(id=identifiant_utilisateur)
    notifications, notifications_actives, notifications_new = user_notification(identifiant_utilisateur)
    message, type_message = message_alerte(request)
    nom_page = "Mes Défis"
    
    
    teamcc = Utilisateur.objects.get(username = "@teamcc")
    prive = False
    defi = Defi.objects.filter(defieur = teamcc, etat="AV", prive = prive).order_by('-date_execution')[:1]
    nb = len(defi)
           
    return render(request, 'CC/arene/defi_moderation_vide.html', locals())

def arene_defi_map (request, id_defi):
    
    identifiant_utilisateur = request.user.id
    utilisateur = Utilisateur.objects.get(id=identifiant_utilisateur)
    
    id_defi = int(request.GET['id_defi'])
    libelle_defi = Libelle_Defi.objects.get(id=id_defi)
    
    eclairs = utilisateur.eclairs
    
    if eclairs < 1 :
        request.session['message'] = "Vous n'avez plus d'éclair pour vous challengez vous-même, modérez des défis, achetez des éclairs ou attendez demain pour pouvoir recommencer à vous défier vous-même."
        request.session['type_message'] = "alert-danger"
        return redirect(user_dashboard)
    
    else :
        aujourdhui = datetime.now()
        teamCC = Utilisateur.objects.get(username = "@teamcc")
        prive = False
        
        
        defi = Defi(libelle=libelle_defi, prive=prive, etat="A", challengeur=utilisateur, enjeu_perso = "Sans Enjeu", defieur=teamCC, date_envoie = aujourdhui, date_acceptation = aujourdhui)
        defi.save()
        
        utilisateur.eclairs = utilisateur.eclairs - 1
        utilisateur.save()
        
        lien = "/arene/defi/?id_defi="+ str(defi.id)
        
        request.session['message'] = "Vous venez de vous défier : " + defi.libelle.nom
        request.session['type_message'] = "alert-success"
        
    return redirect(lien)


@login_required(login_url='/connexion')
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
        if enjeu == "" :
            enjeu = "Sans Enjeu"
        
    except :
        enjeu = "Sans Enjeu"
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

@login_required(login_url='/connexion')
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
    
@login_required(login_url='/connexion')
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

@login_required(login_url='/connexion')
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
            
            image_field = f
            image_file = BytesIO(image_field.read())
            image = Image.open(image_file)
    
            
            image = resizeimage.resize_width(image, 600)
            
            image_file = BytesIO()
            image.save(image_file, 'JPEG', quality=90)
            
            
            preuve = Preuve(nom = nom_preuve, fichier = image)
            preuve.save()
            defi.preuve.add(preuve)
            defi.save()
            

           
    defi.save()
    
    lien = "/arene/defi/?id_defi="+ str(defi.id)
    message = str(utilisateur.username) + " a réalisé votre défi, venez le valider"
    notification = Notification (lien = lien, type='D', message=message, recepteur=defi.defieur, auteur=utilisateur, date = datetime.now())
    notification.save()  
    
    return redirect('/arene/defi/?id_defi='+ str(defi.id))


@login_required(login_url='/connexion')
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
    if defi.libelle.theme.nom == "Elite" :
        defi.challengeur.score_elite =  defi.challengeur.score_elite + defi.libelle.recompense.points
    if defi.libelle.theme.nom == "Citoyen" :
        defi.challengeur.score_citoyen =  defi.challengeur.score_citoyen + defi.libelle.recompense.points
    if defi.libelle.theme.nom == "Création" :
        defi.challengeur.score_creation =  defi.challengeur.score_creation + defi.libelle.recompense.points
    if defi.libelle.theme.nom == "Autre" :
        defi.challengeur.score_autre =  defi.challengeur.score_autre + defi.libelle.recompense.points
    if defi.libelle.theme.nom == "Gaming" :
        defi.challengeur.score_gaming =  defi.challengeur.score_gaming + defi.libelle.recompense.points
    
    defi.challengeur.save()
    
    defi.etat = "V"
    defi.date_validation = datetime.now()
    defi.save()
    
    lien = "/arene/defi/?id_defi="+ str(defi.id)
    message = str(defi.defieur.username) + " a validé votre défi"
    notification = Notification (lien = lien, type='D', message=message, recepteur=defi.challengeur, auteur=utilisateur, date = datetime.now())
    notification.save()  
   
    if defi.prive == False :
        
        message = str (defi.challengeur.username +" a relevé le défi de "+ defi.defieur.username + " haut la main! Il devait : " +defi.libelle.nom)
        lien = "/arene/defi/?id_defi="+str(defi.id)
        actu = Actualite(message = message, nom = "Defi", personne_concernee =  defi.challengeur, lien = lien)
        actu.save()
        
    teamcc = Utilisateur.objects.get(username = "@teamcc")
    
    if defi.defieur == teamcc :
        utilisateur.eclairs = utilisateur.eclairs +1
        utilisateur.save()
        return redirect(user_dashboard)
        
    return redirect('/arene/defi/?id_defi='+ str(defi.id))

@login_required(login_url='/connexion')
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
        
        utilisateur.score_absolu = utilisateur.score_absolu + defi.libelle.recompense.points
        utilisateur.save()
        
        if defi.prive == False :
        
            message = str (defi.challengeur.username +" n'a pas réussi le défi de "+ defi.defieur.username + " : " +defi.libelle.nom)
            lien = "/arene/defi/?id_defi="+str(defi.id)
            actu = Actualite(message = message, nom = "Defi", personne_concernee =  defi.challengeur, lien = lien)
            actu.save()

    defi.save()
    
    lien = "/arene/defi/?id_defi="+ str(defi.id)
    message = str(defi.defieur.username) + " a contesté votre défi, venez voir pourquoi."
    notification = Notification (lien = lien, type='D', message=message, recepteur=defi.challengeur, auteur=utilisateur, date = datetime.now())
    notification.save()
    
    teamcc = Utilisateur.objects.get(username = "@teamcc")
    
    if defi.defieur == teamcc :
        utilisateur.eclairs = utilisateur.eclairs +1
        utilisateur.save()  
        return redirect(user_dashboard)
    
    return redirect('/arene/defi/?id_defi='+ str(defi.id))

@login_required(login_url='/connexion')
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
        
        
        defi.signalement = signalement
        defi.save()

    defi.save()
    
    lien = "/arene/defi/?id_defi="+ str(defi.id)
    message = str(utilisateur.username) + " a signaler un abus de contestation votre défi."
    notification = Notification (lien = lien, type='D', message=message, recepteur=defi.challengeur, auteur=utilisateur, date = datetime.now())
    notification.save()  
    
    return redirect('/arene/defi/?id_defi='+ str(defi.id))

def arene_defi_expiration (request):

    maintenant = datetime.now()
    teamcc = Utilisateur.objects.get(username = "@teamcc")
    
    #Test des défis envoyé
    defis = Defi.objects.filter(expire = False).exclude(defieur = teamcc)
    defis_expiration = []
    
    for defi in defis :
        if defi.etat == "A" :
            
            nb_mins = defi.libelle.duree_execution
            jour_verification = timedelta (minutes = nb_mins)
            date_limite = defi.date_acceptation + jour_verification
            
            if maintenant.replace(tzinfo=pytz.UTC) >= date_limite.replace(tzinfo=pytz.UTC) :
                defis_expiration.append(defi.id)
                
        elif defi.etat == "AV" :
            
            jour_verification = timedelta (days = 2)
            date_limite = defi.date_execution + jour_verification
            
            if maintenant.replace(tzinfo=pytz.UTC) >= date_limite.replace(tzinfo=pytz.UTC) :
                defis_expiration.append(defi.id)
                
        elif defi.etat == "E" : 
            
            nb_mins = defi.libelle.duree_acceptation
            jour_verification = timedelta (minutes = nb_mins)
            date_limite = defi.date_envoie + jour_verification
            
            if maintenant.replace(tzinfo=pytz.UTC) >= date_limite.replace(tzinfo=pytz.UTC) :
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