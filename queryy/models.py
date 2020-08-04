from django.db import models
from datetime import date



class Superfamily(models.Model):
	name = models.CharField(max_length=20)

class Family(models.Model):
	name = models.CharField(max_length=20)
	superfamily = models.ForeignKey(Superfamily, on_delete = models.CASCADE)

class DNASeq(models.Model):
	seq = models.TextField()
	length= models.IntegerField()

class Genome(models.Model):
	name= models.CharField(max_length=10)

class DNARecord(models.Model):
	id= models.CharField(max_length = 40, primary_key=True, unique=True)	
	dnaseq = models.ForeignKey(DNASeq,  on_delete = models.CASCADE)
	coords = models.CharField(max_length = 40)
	family = models.ForeignKey(Family, on_delete = models.CASCADE)
	genome = models.ForeignKey(Genome, on_delete = models.CASCADE)

	def GetProteinNamesIDs(self):
		proseq = self.proteinseq.all()

		dic= {}
		for ps in proseq:
			pn = ps.proteinname.name
			psid = ps.id
			pnid = ps.proteinname.id

			if pn in list( dic.keys() ):
				dic[pn]["psids"].append(psid)
			else:
				dic[pn] = {"psids":[psid], "pnid": pnid}

		return dic

class ProteinName(models.Model):
	name = models.CharField(max_length=20)
	combined= models.BooleanField()
	superfamily = models.ForeignKey(Superfamily, on_delete=models.PROTECT)
	last_checked_uniprot = models.DateField(blank=True, null=True)
	uniprot_new_seq = models.TextField(blank=True, null=True)
	function_updated = models.DateField(blank=True, null=True)
	sequence_updated = models.DateField(blank=True, null=True)
	uniprot_accession = models.CharField(max_length=10)
	uniprot_link = models.URLField(max_length=200, blank=True, null=True)
	base_sequence = models.TextField(blank=True, null=True)
	function = models.TextField(blank=True, null=True)

	def UpdateBaseSequence (self):
		if self.uniprot_new_seq:
			self.base_sequence = self.uniprot_new_seq
			self.uniprot_new_seq = None
			self.save()
		else:
			raise Exception("No new sequence available in database.")


class ProteinSeq(models.Model):
	seq = models.TextField()
	proteinname = models.ForeignKey(ProteinName, on_delete = models.CASCADE)
	length= models.IntegerField()
	dnarecord = models.ForeignKey(DNARecord, on_delete = models.CASCADE, related_name="proteinseq")