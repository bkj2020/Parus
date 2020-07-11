# *** Include Django belong classes ***
from django.shortcuts import render
from django.views.generic.list import View
from django.views.generic import ListView
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
import datetime
#from .models import Country, Hot_book, Hot_room, Hot_guest
# *** Include Global python classes ***
import io
import json
import logging
from xlsxwriter.workbook import Workbook

# Create your views here.
# Create your views here.
class BasePage(View):
    template_name = 'index.html'

    def get(self, request):
        return render(request, 'index.html')
