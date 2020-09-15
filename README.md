Retrobase is a Django-based web application with a database of retrotransposon DNA records, with protein sequences predicted from the DNA 
sequences, at its core.


The DNA data was acquired from UCSC Table Browser. To predict the protein sequences I translated the DNA sequences to amino acid sequences 
in python and created a BLAST database from these amino acid sequences, then I ran Psi-BLAST locally against this database using retrotransposon protein 
sequences obtained from uniprot.



Detailed instructions on acquiring the data are availabile: /assets/Acquiring_data.pdf

Instructions are included on how to upload a small example dataset.



To run the application locally, clone the repository, navigate to the directory containing manage.py and run:


  python manage.py makemigrations

  python manage.py migrate

Then, once you have uploaded some data, following the instructions at /assets/Acquiring_data.pdf, run:

  python manage.py runserver

and navigate to http://localhost:8000/ in your browser.

  
