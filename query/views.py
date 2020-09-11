from django.shortcuts import render
from django.http import HttpResponse
from .models import *
from django.views.generic import ListView, DetailView
from query.forms import SequenceQueryForm
from django.core.exceptions import ValidationError
from Bio import AlignIO
import os



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
		#Add new context
		context['families'] = Family.objects.filter(superfamily=context["object"].id).order_by("name")
		return context

class ProteinFamilyDetailView(DetailView):
	model= Family

class ProteinSeqDetailView(DetailView):
	model= ProteinSeq



	#Get multiple sequence alignment
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		protein_name_instances = context["object"].proteinname_set.all()

		alignments=[]
		for protein_name_instance in protein_name_instances:
			
			#Get protein and superfamily names
			protein_name = protein_name_instance.name
			superfamily = protein_name_instance.superfamily.name

			
			#get msa file
			alignment_filename = protein_name + ".clustal_num"

			module_dir = os.path.dirname(__file__)  # get current directory
			file_path = os.path.join(module_dir, "data", "msa", alignment_filename)

			msa_file = open(file_path, "r")

			#Get alignment length
			align = AlignIO.read (file_path, 'clustal')
			align_len = len(align)

			#extract alignment data
			records=[]
			count= 0
			for line in msa_file:

				if line.startswith(superfamily) or line.startswith(protein_name):
					count+=1

					entry={}
					line = line.split()
					entry["id"] = line[0]
					entry["seq"] = line[1]
					records.append(entry)

					if count % align_len ==0:
						entry={}
						entry["id"] = "|"
						entry["seq"] = " "
						records.append(entry)

			records= records[:-1]

			alignment = {"protein_name": protein_name, "records": records, "align_len": align_len}
			alignments.append(alignment)
		context['alignments'] = alignments
		return context





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

    # If this is a POST request create the default form.
	else:
		form = SequenceQueryForm()

		context = {
	    	'form': form
		}

		return render(request, 'query/query_page.html', context)


def MainSearchBar(request):
    
    # If this is a POST request then process the Form data
	if request.method == 'POST':
		try:
			search_input=request.POST.get("search_input")

			protein_names = ProteinName.objects.filter(name__contains=search_input)
			family = Family.objects.filter(name__contains=search_input)
			superfamily = Superfamily.objects.filter(name__contains=search_input)

			context= {
				"protein_names": protein_names, 
				"family" : family, 
				"superfamily": superfamily,
				"search_input": search_input
			}

			return render(request, 'query/mainsearchbarresults.html', context)
		except Exception as e:
			context = {"error": e}
			return render(request, 'query/mainsearchbarresults.html', context)
