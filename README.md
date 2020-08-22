Retrobase is a Django-based web application with a database of retrotransposon DNA records, with protein sequences predicted from the DNA 
sequences, at its core.

The DNA data was acquired from UTC Table Browser. To predict the protein sequences I created a BLAST database from the DNA data and ran 
Psi-BLAST locally against this database using retrotransposon protein sequences obtained from uniprot. 

A link to the uniprot record used for a given protein is available on the detail page for that protein.

To explore, simply clone the repository, navigate to directory containing manage.py and run:

  python manage.py runserver
  


  
