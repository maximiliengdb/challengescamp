from django.conf.urls import url
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from . import views 


admin.site.site_header = "Challenges.Camp Administration" 

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.home, name='home'),
    
    
    url(r'^inscription', views.inscription, name='Inscription'),
    url(r'^connexion', views.connexion, name='Connexion'),
    url(r'^deconnexion', views.deconnexion, name='Deconnexion'),
    url(r'^recherche$', views.recherche, name='Recherche'),
    
    url(r'^compte/vestiaire/', views.user_dashboard, name='Dashboard'),
    url(r'^compte/parametre/changement_pp' , views.user_changement_pp, name='Changement PP'),
    url(r'^compte/parametre/changement_pa' , views.user_changement_pa, name='Changement PA'),
    url(r'^compte/parametre/changement_mdp', views.user_changement_mdp, name='Profil Settings Page'),
    
    url(r'^compte/map/$', views.user_map, name='Map'),
    url(r'^compte/map_preload/$', views.user_map_preload, name='Map'),
    url(r'^compte/map_tri/', views.user_map_tri, name='Map'),
    url(r'^compte/map_error/$', views.user_map_error, name='Map'),
    url(r'^user_position_push/(?P<id_user>)(?P<longitude>)(?P<latitude>)$' , views.user_map_push_position, name='Map'),
    url(r'^user_position/(?P<id_user>)$' , views.user_map_track_user, name='Map'),
    url(r'^user_position_me/(?P<id_user>)$' , views.user_map_track_me, name='Map'),
    
    url(r'^compte/map/defi/(?P<id_defi>)$', views.arene_defi_map, name='Map'),
    
    url(r'^compte/profil_prive/', views.user_profil_prive, name='Profile'),
    url(r'^compte/profil_public/(?P<profil>)$', views.user_profil_public, name='Proposition Defi'),
    url(r'^compte/mes_amis', views.user_amis, name='Amis Page'),
    url(r'^compte/mes_defis', views.user_defis, name='Defis Page'),
    url(r'^compte/proposition_defi$', views.user_proposition_defi, name='Proposition Defi'),
    url(r'^compte/proposition_defi_etat$', views.user_proposition_defi_etat, name='Proposition Etat'),
    url(r'^compte/demande_ami/page', views.user_demande_ami_page, name='Demande Ami'),
    url(r'^compte/classements', views.user_classement, name='Classement'),
    
    url(r'^compte/notification/', views.user_notification, name='Notification'),
    url(r'^compte/notification_page/', views.user_notification_page, name='Notification'),
    url(r'^compte/vue_notification/', views.user_notification_vue, name='Notification Vue'),
    url(r'^compte/active_notification/(?P<notif_id>)$', views.user_notification_active, name='Notification Active'),
    
    url(r'^validationemail/(?P<id_user>)$', views.user_validation_email, name='Validation Email'),
    
    url(r'^compte/demande_ami/(?P<id_ami>)$', views.user_demande_ami, name='Demande Ami'),
    url(r'^compte/ajout_ami/(?P<id_ami>)$', views.user_ajout_ami, name='Ajout Ami'),
    url(r'^compte/refu_ami/(?P<id_ami>)$', views.user_ajout_ami, name='Ajout Ami'),
    
    url(r'^compte/proposition_defi$', views.user_proposition_defi, name='Proposition Defi'),
    
    url(r'^arene/accueil$', views.arene_accueil, name='Arene'),
    url(r'^arene/defi_lance$' , views.arene_defi_lance, name='Arene'),
    url(r'^arene/defi_page/(?P<id_defi>)$' , views.arene_accueil_defi, name='Arene'),
    url(r'^arene/defi_user_cible/(?P<id_user>)$' , views.arene_defi_cible, name='Arene'),
    url(r'^arene/defi/(?P<id_defi>)$' , views.arene_defi_page, name='Arene'),
    url(r'^arene/defi_accepte/(?P<id_defi>)$' , views.arene_defi_accepte, name='Arene'),
    url(r'^arene/defi_refuse/(?P<id_defi>)$' , views.arene_defi_refuse, name='Arene'),
    url(r'^arene/defi_valide/(?P<id_defi>)$' , views.arene_defi_valide, name='Arene'),
    url(r'^arene/defi_preuve$' , views.arene_defi_preuve, name='Arene'),
    url(r'^arene/defi_contestation$' , views.arene_defi_conteste, name='Arene'),
    url(r'^arene/defi_signalement$' , views.arene_defi_signale, name='Arene'),
    
    url(r'^arene/defi_moderation$' , views.arene_defi_page_moderation, name='Arene'),
    url(r'^arene/defi_moderation_vide$' , views.arene_defi_page_moderation_vide, name='Arene'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 