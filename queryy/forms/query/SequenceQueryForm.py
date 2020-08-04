from django import forms


class QueryForm(forms.Form):
	seq = forms.CharField(help_text='Enter sequence...', required=True)
	model = forms.ChoiceField(choices=[ ("dnaseq", "DNA Sequence"), ("protseq", "Protein Sequence")] )