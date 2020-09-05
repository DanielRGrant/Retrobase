from django.urls import path
from . import views
from .views import *
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
	path('', views.home, name="query-home"), 
	path('query/', views.Query, name="query-query"), 
	path('dnarec/<pk>/', DNADetailView.as_view(), name="query-dnarecinfo"),
	path('protnameinfo/<pk>/', ProteinNameDetailView.as_view(), name="query-proteinnameinfo"),
	path('superfamilyinfo/<pk>/', ProteinSuperfamilyDetailView.as_view(), name="query-proteinsuperfamilyinfo"),
	path('familyinfo/<pk>/', ProteinFamilyDetailView.as_view(), name="query-proteinfamilyinfo"),
	path('protseqinfo/<pk>/', ProteinSeqDetailView.as_view(), name="query-proteinseqinfo"),
	path('BLASTDNAsearch/', views.BLASTDNAsearch, name="query-BLASTdnasearch"),  
	path('mainsearchbarresults/', views.MainSearchBar, name="query-MainSearchBarResults"), 
]

urlpatterns+= staticfiles_urlpatterns()