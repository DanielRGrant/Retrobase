import click
import xml.etree.ElementTree as ET
import os
import itertools
import sqlite3
import json
from Bio import SeqIO
from Bio.SeqRecord import SeqRecord
from datetime import date
from Bio import SeqIO
from Bio.SeqRecord import SeqRecord


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
    return(hit_id)


@click.group()
def retrobase():
    pass

@retrobase.command('translate')
@click.option('--input_file', default=None, type = str,
    help='''Specify input filename. File must be FASTA format, DNA sequences, input filename should be 
    <superfamily>.fasta''')
def translate(input_file):

    output_file = input_file.split(".")[0] + "_prot.fasta" #filename should be <superfamily>_prot.fasta

    try:
        if not is_file_fasta(input_file):
            print("Error: input file must be fasta format")
            return
    except:
        print("Error: file not found")
    
    f=open(input_file, "r")
    seqrecords = SeqIO.parse(f, "fasta")


    std_table = 1 # translate using the standard translation table
    min_pro_len = 100
    seqrec_lst= []
    countid=0
    countrec=-1
    print("Translating file")
    for record in seqrecords:
            countrec+=1
            for strand, nuc in [(+1, record.seq), (-1, record.seq.reverse_complement())]:
                for frame in range(3):
                    length = 3 * ((len(record)-frame) // 3) # Make multiple of 3 (codons have 3 bases) 
                    seqperfr_id = -1 #to count num seqs per open reading frame (ORF)
                    for pro in nuc[frame:frame+length].translate(std_table).split("*"): #Translate using SeqRecord.translate and iterate over potential ORFs
                        seqperfr_id +=1 #count num seqs per ORF to make unique id
                        if len(pro) >= min_pro_len:
                            fam= record.id.split('_')[2] #get subfamily name
                            descr = "rec_id=" + str(countrec) + " fam=" + fam + " length=" + str(len(pro))+ " strand=" + str(strand) + " frame=" + str(frame)
                            Seqid = str(countrec) + "_" + str(strand) + "_" + str(frame)+ "_" + str(seqperfr_id) + "_" + fam 
                            countid+=1
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
def assign_proteins(dna_input_file, protein_input_file, outputfile, superfamily, protein_names, genome):

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

            protein_dic[pn] = gethits(r"C:\Users\Dan\dev\retrobase\data\{}_psiblast.txt".format(pn))
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
        


    print("Collecting DNA record data")    

    #get dna record data
    file = open(dna_input_file, 'r')
    record = SeqIO.parse(file, "fasta")

    record_count=-1
    dna_recs = {}
    for rec in record:
        
        #create record id
        record_count+=1 
        dnarecid= str(record_count) + "_" + superfamily
        
        #add DNA record data
        coords = rec.description.split(" ")[1].split("=")[1]
        family = rec.id.split("_")[2]
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
        


    print("Collecting protein record data") 
        
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
                spl = rec.id.split("_")
                dnarecid = spl[0]+ "_" + superfamily
                
                if ( dna_recs[dnarecid]["protdata"] == None ):
                    dna_recs[dnarecid]["protdata"]= {}
                
                #hex count numbers
                hex_record_count = hex(record_count)[2:]
                hex_protein_count = hex(protein_count)[2:]
                protseqid = "{0} - {1} - {2}".format(superfamily.upper(),  str(hex_record_count), hex_protein_count)   #### fix id ####
                entry= {}
                entry["pep_seq"] = str(rec.seq)
                entry["pep_length"] = len( str(rec.seq) )
                entry["protname"]= protname
                

                dna_recs[dnarecid]["protdata"][protseqid]= entry    

    count=0
    test_dic={}
    for k,v in dna_recs.items():
        test_dic[k]=v                
        count+=1
        if count>100:
            break
    print("Writing JSON file")
    try:
        with open(outputfile, 'w') as outfile:
            json.dump(test_dic, outfile)

            print("Completed!")
    except:
        print("Error: could not write file.")




if __name__ == "__main__":
    retrobase()






