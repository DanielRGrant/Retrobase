Retrobase is a Django-based web application with a database of retrotransposon DNA records, with protein sequences predicted from the DNA 
sequences, at its core.


The DNA data was acquired from UCSC Table Browser. To predict the protein sequences I translated the DNA sequences to amino acid sequences 
in python and created a BLAST database from these amino acid sequences, then I ran Psi-BLAST locally against this database using retrotransposon protein 
sequences obtained from uniprot.


Detailed instructions on acquiring the data are availabile: /assets/Acquiring_data.pdf



To explore, simply clone the repository, navigate to directory containing manage.py and run:

  python manage.py runserver
 
Then follow the instructions on populating the database in /assets/Acquiring_data.pdf
A small JSON file is provided with the code to upload the contained data.

  
