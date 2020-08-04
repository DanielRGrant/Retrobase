from django.shortcuts import render
from django.http import HttpResponse
from .models import *
from django.views.generic import DetailView
from django.core.exceptions import ValidationError


def home(request):
	
	return render(request, 'ExpressionAtlas/expression_atlas_page.html')	