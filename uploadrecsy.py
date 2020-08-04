import json
from query.models import *
import signal


class GracefulExiter():
	#https://stackoverflow.com/questions/24426451/how-to-terminate-loop-gracefully-when-ctrlc-was-pressed-in-python/24426816
    def __init__(self):
        self.state = False
        signal.signal(signal.SIGINT, self.change_state)

    def change_state(self, signum, frame):
        print("Exiting after current record (repeat to exit immediately)")
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        self.state = True

    def exit(self):
        return self.state





def GetJSONData(filename):
	with open(filename) as f:
		return json.load(f)

#for uploading dna record
def UploadDNARec(data, filein=True):
	if (filein):
		data = GetJSONData(data)

	dna_recs = data["dna_recs"]
	ids = list( dna_recs.keys() )[0:400]


	flag = GracefulExiter()
	for i in ids:
		r = dna_recs[i]

		sf = Superfamily.objects.filter(name= r["superfam"]) #check if sf name is already in db
		if (len( sf ) ==0):
			sfrec = Superfamily( name= r["superfam"]) #if sf not in db, add
			sfrec.save()
			sfid = Superfamily.objects.filter(name= r["superfam"])[0]
		else:
			sfid = sf[0]

		fam = Family.objects.filter(name= r["family"]) #check if fam name is already in db
		if (len( fam ) ==0):
			famrec = Family( name= r["family"], superfamily = sfid) #if fam not in db, add 
			famrec.save()
			famid = Family.objects.filter(name= r["family"])[0]
		else:
			famid= fam[0]


		dnaseq = DNASeq.objects.filter(seq= r["dna_seq"]) #check if prot name is already in db
		if (len( dnaseq ) ==0):
			dnaseqrec = DNASeq( seq= r["dna_seq"], length = r["dna_length"]) #if protein not in db, add 
			dnaseqrec.save()
			dnaseqid = DNASeq.objects.filter(seq= r["dna_seq"])[0]
		else:
			dnaseqid = dnaseq[0]

		genome = Genome.objects.filter(name= r["genome"]) #check if prot name is already in db
		if (len( genome ) ==0):
			genomerec = Genome( name= r["genome"]) #if protein not in db, add 
			genomerec.save()
			genomeid = Genome.objects.filter(name= r["genome"])[0]
		else:
			genomeid = genome[0]


		dnarecDBid = DNARecord.objects.filter(id=r["dnarecid"])
		if( len (dnarecDBid) ==0):
			dnarec= DNARecord(
							id=r["dnarecid"], 
							coords= r["coords"], 
							genome= genomeid, 
							dnaseq= dnaseqid, 
							family = famid, 
							)
			dnarec.save()
			dnarecDBid = DNARecord.objects.filter(id=r["dnarecid"])[0]
		else:
			dnarecDBid= dnarecDBid[0]


		print("loop1")


		if ( r["protdata"] == None ):
			if flag.exit():
				break
			continue


		protkeys = list( r["protdata"].keys() )

		for k in protkeys:
			print("loop2")
			p = r["protdata"][k]

			protname = ProteinName.objects.filter(name= p["protname"]) #check if prot name is already in db
			if (len( protname ) ==0):

				try:
					p["combined"]
					comb=True
				except:
					comb=False
				protnamerec = ProteinName( name= p["protname"], superfamily = sfid, combined= comb) #if protein not in db, add 
				protnamerec.save()
				protnameid = ProteinName.objects.filter(name= p["protname"])[0]
			else:
				protnameid=protname[0]


			protseq = ProteinSeq.objects.filter(seq= p["pep_seq"]) #check if prot name is already in db
			if (len( protseq ) ==0):
				pepseqrec = ProteinSeq( seq= p["pep_seq"], proteinname= protnameid, length = p["pep_length"], dnarecord = dnarecDBid) #if protein not in db, add 
				pepseqrec.save()
				pepseqid = ProteinSeq.objects.filter(seq= p["pep_seq"])[0]
			else:
				protseqid = protseq[0]


			if flag.exit():
				break




