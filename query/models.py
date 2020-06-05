from django.db import models




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

	def GetProteinNames(self):
		proseq = self.proteinseq.all()
		if ( len( proseq ) == 0):
			return "None Predicted"
		pncount = {}
		for ps in proseq:
			pname = ps.proteinname.name
			if ( pname in list( pncount.keys() ) ):
				pncount[pname] +=1
			else: 
				pncount[pname] = 1

		output=""
		for pn in list( pncount.keys() ):
			output = "{}{} ({}), ".format(output, pn, pncount[pn])
		return output[0: len(output)-2]
	
class ProteinName(models.Model):
	name = models.CharField(max_length=20)
	combined= models.BooleanField()

class ProteinSeq(models.Model):
	seq = models.TextField()
	proteinname = models.ForeignKey(ProteinName, on_delete = models.CASCADE)
	length= models.IntegerField()
	dnarecord = models.ForeignKey(DNARecord, on_delete = models.CASCADE, related_name="proteinseq")