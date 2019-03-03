from stark.service.stark import starkSite,ModelStark

from .models import *
from django.utils.safestring import mark_safe
from django.conf.urls import url
from django.http import JsonResponse

from django.shortcuts import HttpResponse, redirect, render

starkSite.register(User)
starkSite.register(Role)

class PermissionConfig(ModelStark):
    list_display= ["title","url","group","action"]

starkSite.register(Permission,PermissionConfig)
starkSite.register(PermissionGroup)





