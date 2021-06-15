from django.http import request
from vehicles.models import Customer, Mechanic, Request
from django.contrib import admin
from vehicles import *
# Register your models here.
admin.site.register((Customer,Mechanic,Request))