# -*- coding: utf-8 -*-

from django import forms
from CC.models import Utilisateur, Photo
from django.forms.widgets import Widget

class Formulaire_Inscription(forms.ModelForm):
    class Meta:
        model = Utilisateur
        fields = [ 'username', 'email', 'password',  'first_name', 'last_name']
        widgets = {
            'username' : forms.TextInput (attrs={'class': 'form-control', 'placeholder': 'Pseudo'}),
            'email' : forms.TextInput (attrs={'class': 'form-control', 'type' : 'email', 'placeholder': 'E-mail'}),
            'password' : forms.TextInput (attrs={'class': 'form-control', 'type':'password', 'placeholder': 'Mot de Passe'}),
            'first_name' : forms.TextInput (attrs={'class': 'form-control', 'placeholder': 'Prénom'}),
            'last_name' : forms.TextInput (attrs={'class': 'form-control', 'placeholder': 'Nom'}),
        }
        
        labels ={
            'username' : (''),
            'email' : (''),
            'password' : (''),
            'first_name' : (''),
            'last_name' : (''),
  
            }
        help_texts = {
            
            'username' : (''),
            
            }
        
class Formulaire_Import_Image (forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['image']
        

class Formulaire_Change_MDP(forms.Form):
    password = forms.CharField(label='', widget=forms.TextInput (attrs={'class': 'form-control', 'type':'password', 'placeholder': 'Mot de passe'}), required=True)
    password2 = forms.CharField(label='',widget=forms.TextInput (attrs={'class': 'form-control', 'type':'password', 'placeholder': 'Confirmation mot de passe'}), required=True)
 