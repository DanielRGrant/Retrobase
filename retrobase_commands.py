import click
import urllib3
import xml.etree.ElementTree as ET
import os
import sys
import itertools
import sqlite3
import json
import django
import signal
from Bio import SeqIO
from Bio.SeqRecord import SeqRecord
from datetime import date
from Bio import SeqIO
from Bio.SeqRecord import SeqRecord



#Get models

try:
    sys.path.append(r"C:\Users\Dan\dev\retrobase\app\retrobase")
except:
    pass

try:
    os.environ['DJANGO_SETTINGS_MODULE'] = 'retrobase.settings'
    django.setup()
    from query.models import *
    from django.conf import settings
except:
    print("Could not connect retrieve models. Check that path to django base directory is in Python path")
    quit()



def is_file_fasta(filename):
    
    with open(filename) as file:
        x = SeqIO.parse(file, 'fasta')
        try:
            next(x)
            return True
        except StopIteration:
            return False
        except:
            raise

        file.close()


def intersection(lst1, lst2): 
    '''Get intsersection of 2 lists'''
    lst3 = [value for value in lst1 if value in lst2] 
    return lst3


def gethits(filename):
    '''Extact hits from psi-blast XML file with e value above given value'''
    file = open(filename, "r")

    tree= ET.parse(file)
    root=tree.getroot()
    
    hits = []
    for h in root.iter('Hit'):
        hit_id = h.find('Hit_id').text
        hits.append(hit_id)
    return(hits)


class GracefulExiter():
    #https://stackoverflow.com/questions/24426451/how-to-terminate-loop-gracefully-when-ctrlc-was-pressed-in-python/24426816
    #finish iteration if user terminates justs once
    def __init__(self):
        self.state = False
        signal.signal(signal.SIGINT, self.change_state)

    def change_state(self, signum, frame):
        print("Exiting after current record (repeat to exit immediately)")
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        self.state = True

    def exit(self):
        return self.state


def GetUniprotData(ID):

    #Collect data from Uniprot
    http = urllib3.PoolManager()
    url = "https://www.uniprot.org/uniprot/{}.xml".format(ID)
    r = http.request('GET', url)

    urllib3_status_report = {200: "The request was processed successfully.",
    400: "Bad request. There is a problem with your input.",
    404: "Not found. The resource you requested doesn't exist.",
    410: "Gone. The resource you requested was removed.",
    500: "Internal server error. Most likely a temporary problem, but if the problem persists please contact us.",
    503: "Service not available. The server is being updated, try again later."}


    #if GET request fails, raise exception
    if(r.status!= 200):
        report = urllib3_status_report[r.status]
        raise Exception(report)

    data = r.data

    root = ET.fromstring(data)

    #get function text
    el = root.findall(".//{http://uniprot.org/uniprot}entry/{http://uniprot.org/uniprot}comment/[@type='function']/{http://uniprot.org/uniprot}text")
    functiontext = el[0].text

    #get sequence
    el = root.findall(".//{http://uniprot.org/uniprot}entry/{http://uniprot.org/uniprot}sequence")
    sequencetext = el[0].text
    
    output= {"function": functiontext, "sequence": sequencetext}
    return output


@click.group()
def retrobase():
    pass

@retrobase.command('translate')
@click.option('--input_file', default=None, type = str,
    help='''Specify input filename. File must be FASTA format, DNA sequences, input filename should be 
    <superfamily>.fasta''')
@click.option('--output_file', default=None, type = str,
    help='''Specify output filename and path. Should end in .fasta''')
@click.option('--superfamily', default=None, type = str,
    help='''Specify superfamily/class of RT sequences''')
def translate(input_file, output_file, superfamily):

    try:
        if not is_file_fasta(input_file):
            print("Error: input file must be fasta format")
            quit()
    except:
        print("Error: file not found")
        quit()
    try:
        assert superfamily != None
    except:
        print("Error: missing superfamily parameter")
        quit()
    

    f=open(input_file, "r")
    seqrecords = SeqIO.parse(f, "fasta")

    file_name = os.path.basename(input_file)
    print("Translating file:", file_name)

    std_table = 1 # translate using the standard translation table
    min_pro_len = 100
    seqrec_lst= []
    countrec=-1

    for record in seqrecords:
            countrec+=1
            count_per_record = 0
            for strand, nuc in [(+1, record.seq), (-1, record.seq.reverse_complement())]: #get seq of both strands

                for frame in range(3):
                    length = 3 * ((len(record)-frame) // 3) # Make multiple of 3 (codons have 3 bases) 
                    seqperfr_id = -1 #to count num seqs per open reading frame (ORF)
                    for pro in nuc[frame:frame+length].translate(std_table).split("*"): #Translate using SeqRecord.translate and iterate over potential ORFs
                        seqperfr_id +=1 #count num seqs per ORF to make unique id
                        if len(pro) >= min_pro_len:
                            count_per_record +=1

                            ### Create protein sequence record ###
                            fam= record.id.split('_')[2] #get subfamily name
                            descr = "rec_id=" + str(countrec) + " fam=" + fam + " length=" + str(len(pro))+ " strand=" + str(strand) + " frame=" + str(frame) + "# sequence in frame=" + str(seqperfr_id)
                        
                            # Create protein seq id
                            dna_id = hex(countrec) [2:]
                            prot_id = hex(count_per_record) [2:]
                            Seqid = superfamily.upper() + "-" + dna_id + "-" + prot_id

                            # Add record to list
                            seqrec_lst.append(SeqRecord(seq= pro,
                                                        id=Seqid,
                                                        name= fam,
                                                        description= descr
                                                        )
                                             )
                            

    SeqIO.write(seqrec_lst, output_file, "fasta")
    print("File translated")



@retrobase.command('assign_proteins')
@click.option('--dna_input_file', type = str,
    help='''Provide the path to the fasta file output from UTSC table browser''')
@click.option('--protein_input_file', type = str,
    help='''Provide the path to the fasta created by the tanslate command''')
@click.option('--psiblast_directory', type = str,
    help='''Provide the path to the DIRECTORYpsi-blast output file''')
@click.option('--outputfile', type = str,
    help='''Provide the path and filename for creating the output json file''')     
@click.option('--superfamily', type = str,
    help='''Provide the name of the retrotransposon class''')
@click.option('--protein_names', type = str, multiple=True,
    help='''Provide the names of the proteins identified by psiblast. For multiple proteins
    format as such: 
    --protein_names=<protein1> --protein_names=<protein2> --protein_names=<protein3>''')
@click.option('--genome', type = str,
    help='''Specify the genome build from which the DNA sequences come''')
def assign_proteins(dna_input_file, protein_input_file, psiblast_directory, outputfile, superfamily, protein_names, genome):

    try:
        print(dna_input_file)
    except:
        print("Missing dna_input_file option")
        quit()

    try:
        print(protein_input_file)
    except:
        print("Missing protein_input_file option")
        quit()

    try:
        print(outputfile)
    except: 
        print("Missing outputfile option")
        quit()

    try:
        print(superfamily)
    except:
        print("Missing superfamily option")
        quit()

    try:
        print(protein_names)
    except:
        print("Missing protein_names option")
        quit()

    try:
        print(genome)
    except:
        print("Missing genome option")
        quit()


    protein_dic = {}
    #get ids matched to each protein name
    print("Getting psiblast results")
    for pn in protein_names:
        
        try:
            psiblast_file = os.path.join(psiblast_directory, pn + "_psiblast.txt")
            protein_dic[pn] = gethits(psiblast_file)
        except FileNotFoundError:
            raise Exception("Psiblast output file not found for protein: {}. Must be formatted <protein name>_psiblast.txt".format(pn))
        except:
            raise
        print("Retrieved psiblast results for:", pn)
        
    for name in protein_names:
        print("Number of sequences mapped to {0}: {1}: ".format(name, len(protein_dic[name])))

              
              


    print("Number of instances where multiple proteins were predicted for the same translated protein sequence: ")

    #Check for overlap between protein predictions
    comparisons = list(itertools.combinations(protein_names, 2)) #get all pairwise name combinations of proteins     
    intergroups= {}
    for c in comparisons:
        protein1_list= protein_dic[ c[0] ]
        protein2_list= protein_dic[ c[1] ]
        
        protein1= c[0]
        protein2= c[1]
        
        inter= intersection(protein1_list, protein2_list)
        print( "    {0}-{1}: {2}".format( protein1 , protein2, len(inter)) )
        


    print("Parsing DNA record data")    

    #get dna record data
    file = open(dna_input_file, 'r')
    record = SeqIO.parse(file, "fasta")

    record_count=-1
    dna_recs = {}
    for rec in record:
        
        #create record id
        record_count+=1 
        dnarecid= superfamily + "-" + hex(record_count)[2:]
        
        #add DNA record data
        coords = rec.description.split(" ")[1].split("=")[1]
        family = rec.description.split("_")[2].split(" ")[0]
        entry= {}
        entry["coords"] = coords
        entry["dnarecid"] = dnarecid
        entry["dna_seq"] = str(rec.seq)
        entry["dna_length"] = len( entry["dna_seq"] )
        entry["genome"]= genome
        entry["superfam"] = superfamily
        entry["family"] = family
        # protdata will be overwritten with dictionary of protein seq records if 
        # proteins are identified for this record      
        entry["protdata"] = None 
        
        #attach DNA record entry
        dna_recs[dnarecid] = entry
     

    print("Parsing protein record data") 
        
    #Get protein record data
    file = open(protein_input_file, 'r')
    protrecord = SeqIO.parse(file, "fasta")


    #check if seq record has been identified as a real protein sequence (by psiblast)          
    protein_count=-1
    for rec in protrecord:
        for pn in protein_names:
            if rec.id in protein_dic[pn]:
                protname = pn
                
                protein_count+=1
                spl = rec.id.split("-")
                dnarecid = superfamily + "-" + spl[1]
                
                if ( dna_recs[dnarecid]["protdata"] == None ):
                    dna_recs[dnarecid]["protdata"]= {}
                
                #hex count numbers
                hex_record_count = hex(record_count)[2:]
                hex_protein_count = hex(protein_count)[2:]


                protseqid = "{0}-{1}-{2}".format(superfamily.upper(), hex_record_count, hex_protein_count) #########################
                entry= {}
                entry["pep_seq"] = str(rec.seq)
                entry["pep_length"] = len( str(rec.seq) )
                entry["protname"]= protname
                
                try:
                    dna_recs[dnarecid]["protdata"][protseqid]
                except:
                    dna_recs[dnarecid]["protdata"][protseqid] = []
                
                dna_recs[dnarecid]["protdata"][protseqid].append(entry)




    print("Writing JSON file")
    try:
        with open(outputfile, 'w') as outfile:
            json.dump(dna_recs, outfile)

            print("Completed!")
    except:
        raise
        print("Error: could not write file.")





@retrobase.command('upload_records')
@click.option('--input_file', type = str,
    help='''Provide the path to the json file output by assign_proteins command''')
def UploadRecords(input_file):
    '''for uploading data to database from command line'''

    #Get data
    print("Parsing JSON data")
    try:
        with open(input_file) as f:
            dna_recs= json.load(f)
    except FileNotFoundError:
        print("Error: Could not find file")
        quit()
    except:
        raise
    ids = list( dna_recs.keys() )
    number_recs = len(ids)




    print("Uploading {} records".format(number_recs))
    flag = GracefulExiter() #Finish loop iteration 
    count=0
    for i in ids:
        if count % 100 == 0 and count !=1:
            print("Uploaded {0}/{1} records".format(count, number_recs))
        count+=1
        r = dna_recs[i]

        sf = Superfamily.objects.filter(name= r["superfam"]) #check if sf name is already in db
        if len(sf)==0:
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


        dnaseq = DNASeq.objects.filter(seq= r["dna_seq"]) #check if dna seq is already in db
        if (len( dnaseq ) ==0):
            dnaseqrec = DNASeq( seq= r["dna_seq"], length = r["dna_length"], family=famid) #if dna seq not in db, add 
            dnaseqrec.save()
            dnaseqid = DNASeq.objects.filter(seq= r["dna_seq"])[0]
        else:
            dnaseqid = dnaseq[0]

        genome = Genome.objects.filter(name= r["genome"]) #check if genome is already in db
        if (len( genome ) ==0):
            genomerec = Genome( name= r["genome"]) #if genome not in db, add 
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


        if ( r["protdata"] == None ):
            if flag.exit():
                break
            continue


        protkeys = list( r["protdata"].keys() )

        for protein_seq_id in protkeys:

            for p in r["protdata"][protein_seq_id]:
            
         

                protname = ProteinName.objects.filter(name= p["protname"]) #check if prot name is already in db
                if (len( protname ) ==0):
                    protnamerec = ProteinName.objects.create( name= p["protname"], superfamily = sfid) #if protein not in db, add 
                    protnameid = ProteinName.objects.filter(name= p["protname"])[0]
                else:
                    protnameid=protname[0]



                proteinseq = ProteinName.objects.filter(name= p["protname"], proteinseq__id= protein_seq_id) #check if prot seq is already in db (using manytomany relation)
                
                if (len( proteinseq ) ==0):
                    pepseqrec = protnameid.proteinseq.create(id= protein_seq_id, seq= p["pep_seq"], length = p["pep_length"], dnarecord = dnarecDBid) #if protein not in db, add 
                    pepseqrec.save()
                    pepseqid = ProteinSeq.objects.filter(seq= p["pep_seq"])[0]

                


                if flag.exit():
                    break



@retrobase.command("enter_uniprot_data")
@click.option('--accession_ids', default=None, type = str, multiple=True,
    help='''Specify uniprot accession IDs. For multiple IDs, use tag multiple times''')
@click.option('--protein_names', default=None, type = str, multiple=True,
    help='''Specify protein names, as entered in database, corresponding to the entered accession 
    ids, in same order as accession IDs. For multiple IDs, use tag multiple times''')
def UpdateProteinInfo(accession_ids, protein_names):

    if len(accession_ids) != len(protein_names):
        print('''Unequal number of IDs and protein names entered. Use --help option for more information.''')


    user_input = input("Are you sure the accession numbers and protein names were entered in an identical order? enter y or n: ")

    while True:
        if user_input == "y":
            break
        elif user_input == "n":
            quit()
        else:
            user_input = input("Are you sure the accession numbers and protein names were entered in an identical order? enter y or n: ")


    for i in range(len(accession_ids)):

        #Get individual protein and accession
        ID= accession_ids[i]
        protein_name = protein_names[i]

        #get uniprot data
        uniprotData = GetUniprotData(ID)

        print("Updating data for protein {0} from uniprot entry with accession {1}.".format(protein_name, ID))

        #get database entry
        protname_instance = ProteinName.objects.filter(name=protein_name)[0]
        #enter data to database
        protname_instance.function=uniprotData["function"]
        protname_instance.base_sequence = uniprotData["sequence"]
        protname_instance.uniprot_accession = ID
        protname_instance.uniprot_link = "https://www.uniprot.org/uniprot/" + ID
        protname_instance.last_checked_uniprot = date.today() 
        protname_instance.sequence_updated = date.today()            
        protname_instance.function_updated = date.today()
        protname_instance.save()





if __name__ == "__main__":
    retrobase()