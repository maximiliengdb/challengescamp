# -*- coding: utf-8 -*-

from django.contrib import admin
from CC.models import *
from django.forms import ModelForm

class UtilisateurAdmin(admin.ModelAdmin):
   list_display   = ('username', 'first_name', 'last_name')
   list_filter    = ('username','first_name',)
   ordering       = ('username', )
   search_fields  = ('username', 'first_name')

class DefiAdmin(admin.ModelAdmin):
    list_display   = ('id','libelle', 'defieur', 'challengeur', 'date_envoie', 'etat')
    date_hierarchy = 'date_envoie'
    ordering = ('-date_envoie',)
    search_fields  = ('id', 'libelle', 'etat')
    
    def libelleDefi(self, Defi):    
        return self.libelle.nom
    
    libelle = libelleDefi
    
class libelleDefi(admin.ModelAdmin):
    list_display   = ('nom', 'description', 'theme', 'sous_theme', 'recompense', 'auteur')
    search_fields  = ('nom', 'description', 'theme', 'sous_theme')
    
class libelleMaj(admin.ModelAdmin):
    list_display   = ('date',)
    ordering = ('-date',)
    
class libelleRecompense(admin.ModelAdmin):
    list_display   = ('nom', 'points', 'goodies', 'goodies_description',)
    search_fields  = ('nom', 'points', 'goodies', 'goodies_description',)
   
class libellePropisitionDefi(admin.ModelAdmin):
    list_display   = ('nom', 'description', 'auteur', 'etat',)
    search_fields  = ('nom', 'description', 'auteur', 'etat',)
    
class libelleNotification(admin.ModelAdmin):
    list_display   = ('type', 'message', 'auteur', 'recepteur', 'date',)
    
class libelleMapPoint(admin.ModelAdmin):
    list_display   = ('id_osm', 'nom', 'attribut', 'categorie', 'sous_categorie')
    

admin.site.register(Utilisateur, UtilisateurAdmin),
admin.site.register(Signalement),
admin.site.register(Photo),
admin.site.register(Defi, DefiAdmin),
admin.site.register(Proposition_Defi, libellePropisitionDefi),
admin.site.register(Preuve),
admin.site.register(Libelle_Defi, libelleDefi),
admin.site.register(Theme),
admin.site.register(Sous_Theme),
admin.site.register(Recompense, libelleRecompense),
admin.site.register(Notification, libelleNotification),
admin.site.register(DemandeAmi),
admin.site.register(Contestation),
admin.site.register(MAJ, libelleMaj),
admin.site.register(Libelle_Quete),
admin.site.register(Quete),
admin.site.register(Actualite),
admin.site.register(MapPoint, libelleMapPoint),