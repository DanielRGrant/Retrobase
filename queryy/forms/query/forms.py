from django import forms


class QueryForm(forms.Form):
	forms.CharField(help_text='Enter sequence...', required=True)
	forms.ChoiceField(choices=[ ("dnaseq", "DNA Sequence"), ("protseq", "Protein Sequence")] )