# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.template import RequestContext
from CC.views import *

def mise_a_jour(request) :
    arene_defi_expiration(request)
    eclair_refill(request)
    
    return