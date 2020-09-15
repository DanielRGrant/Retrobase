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

	def __str__(self):
		return str(self.id)

	def GetProteinNamesIDs(self):
		protseqs = self.proteinseq.all()

		dic= {}
		if len(protseqs) > 0: 
			for protseq in protseqs:
				protnames_instances = protseq.proteinname_set.all()
				protseqid = protseq.id

				for protname_instance in protnames_instances:
					protname=protname_instance.name
					protnameid=protname_instance.id

					if protname in list( dic.keys() ): #if protname already added
						dic[protname]["protseqid"].append(protseqid)

					else:
						dic[protname] = {
							"protseqid":[protseqid],
							"protnameid": protnameid
						}

		return dic



class ProteinSeq(models.Model):
	id= models.CharField(max_length = 40, primary_key=True, unique=True)
	seq = models.TextField()
	length= models.IntegerField()
	dnarecord = models.ForeignKey(DNARecord, on_delete = models.CASCADE, related_name="proteinseq")

	def __str__(self):
		return str(self.id)

class ProteinName(models.Model):
	name = models.CharField(max_length=20)
	superfamily = models.ForeignKey(Superfamily, on_delete=models.PROTECT)
	last_checked_uniprot = models.DateField(blank=True, null=True)
	uniprot_new_seq = models.TextField(blank=True, null=True)
	function_updated = models.DateField(blank=True, null=True)
	sequence_updated = models.DateField(blank=True, null=True)
	uniprot_accession = models.CharField(max_length=10)
	uniprot_link = models.URLField(max_length=200, blank=True, null=True)
	base_sequence = models.TextField(blank=True, null=True)
	function = models.TextField(blank=True, null=True)
	proteinseq = models.ManyToManyField(ProteinSeq, blank=True, null=True)

	def __str__(self):
		return self.name

