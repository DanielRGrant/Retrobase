from django.shortcuts import render
from django.http import HttpResponse
from .models import *
from django.views.generic import ListView, DetailView
from query.forms import SequenceQueryForm
from django.core.exceptions import ValidationError


def home(request):
	superfams = Superfamily.objects.all()

	return render(request, 'query/home.html', {"superfams": superfams})

def search(request):
	query= request.GET.get('q')
	model= request.GET.get('queryselect')

	if (model == "protseq"):
		result = ProteinSeq.objects.filter(seq__icontains=query)
		context = {
			'proteins': result,
		}
		return render(request, 'query/search_results.html', context)

	elif (model=="DNAseq"):
		result = DNASeq.objects.filter(seq__icontains=query)
		context = {
			'dnarec': result
		}
		return render(request, 'query/DNAsearch_results.html', context)

##### BLAST QUERY THIS SHIIIIIIIT #####

def BLASTDNAsearch(request):
	query= request.POST.get('q')
	
	context = {
		'dnarec': DNA_record.objects.filter(dnaseq__icontains=query)
	}
	
	return render(request, 'query/DNAsearch_results.html', context)

class DNADetailView(DetailView):
	model= DNARecord

class ProteinNameDetailView(DetailView):
	model= ProteinName

class ProteinSuperfamilyDetailView(DetailView):
	model= Superfamily

	def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
		context = super().get_context_data(**kwargs)
		# Add in a QuerySet of all the books 
		context['families'] = Family.objects.filter(superfamily=context["object"].id).order_by("name")
		return context

class ProteinFamilyDetailView(DetailView):
	model= Family

class ProteinSeqDetailView(DetailView):
	model= ProteinSeq



def Query(request):
    
    # If this is a POST request then process the Form data
	if request.method == 'POST':

	# Create a form instance and populate it with data from the request (binding):
		form = SequenceQueryForm(request.POST, request.FILES)

		# Check if the form is valid:
		if form.is_valid():
		# process the data in form.cleaned_data as required (here we just write it to the model due_back field)
			model = form.cleaned_data['model']
			query = form.cleaned_data['seq']

			



			if (model == "protseq"):
				result = ProteinSeq.objects.filter(seq__icontains=query)
				context = {
					'proteins': result,
				}
				return render(request, 'query/search_results.html', context)

			elif (model=="DNAseq"):
				result = DNASeq.objects.filter(seq__icontains=query)
				context = {
					'dnarec': result
				}
				return render(request, 'query/DNAsearch_results.html', context)


		#If Validation exceptions raised
		else:
			context = {
		    	'form': form
			}
			return render(request, 'query/query_page.html', context)

    # If this is a GET (or any other method) create the default form.
	else:
		form = SequenceQueryForm()

		context = {
	    	'form': form
		}

		return render(request, 'query/query_page.html', context)