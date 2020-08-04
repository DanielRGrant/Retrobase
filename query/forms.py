from django import forms
from django.core.exceptions import ValidationError
import Bio
from Bio import SeqIO

class SequenceQueryForm(forms.Form):
	seq = forms.CharField(required=False, label="Enter Sequence:", widget=forms.Textarea)
	file = forms.FileField(required=False, label="Upload FASTA file:")
	model = forms.ChoiceField(choices=[ ("DNAseq", "DNA Sequence"), ("protseq", "Protein Sequence")] , label="DNA or Protein:")


	def clean(self):
		cleaned_data = super().clean()
		seq = cleaned_data.get("seq").upper()
		model= cleaned_data.get("model")
		file = cleaned_data.get("file")

		#either file or sequence must be submitted
		if not (seq or file):
			raise ValidationError(
				"You must submit a sequence in the text box "
				"or a FASTA file.")

		#extract seq from FASTA file to validate
		if file:
			file= self.cleaned_data["file"]
			f= file.read()
			f= f.decode('utf-8')
			f= f.split("\n")
			for line in f:
				if line.startswith(">"):
					idline = line
				else:
					seq=line

			cleaned_data["seq"] = seq


		#NOTE TO SELF: extract file in here and validate
		if model == "DNAseq":
			for base in seq:
				if not (base in "ACTG"):
					raise ValidationError(
						"DNA sequence must only contain A, T, C and G"
						)

		#all single letter aa symbols
		aminoacids = "GPAVLIMCFYWHKRQNEDST"

		if model == "protseq":
			for base in seq:
				if not (base in aminoacids):
					raise ValidationError(
						"Protein sequence must only contain single letter amino acid symbols"
						)


