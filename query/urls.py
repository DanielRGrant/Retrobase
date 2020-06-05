from django.urls import path
from . import views
from .views import *

urlpatterns = [
	path('', views.home, name="query-home"), 
	path('search/', views.search, name="query-search"), 
	path('querytest/', views.Query, name="query-query"), 
	path('dnarec/<pk>/', DNADetailView.as_view(), name="query-dnarecinfo"),
	path('protnameinfo/<pk>/', ProteinNameDetailView.as_view(), name="query-proteinnameinfo"),
	path('superfamilyinfo/<pk>/', ProteinSuperfamilyDetailView.as_view(), name="query-proteinsuperfamilyinfo"),
	path('familyinfo/<pk>/', ProteinFamilyDetailView.as_view(), name="query-proteinfamilyinfo"),
	path('protseqinfo/<pk>/', ProteinSeqDetailView.as_view(), name="query-proteinseqinfo"),
	path('BLASTDNAsearch/', views.BLASTDNAsearch, name="query-BLASTdnasearch"), 
]