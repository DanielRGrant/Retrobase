import urllib3
import xml.etree.ElementTree as ET
from datetime import date
from query.models import ProteinName

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


def UpdateProteinInfo():
    for nm in ProteinName.objects.all():
        ID= nm.uniprot_accession

        uniprotData = GetUniprotData(ID)
        
        if uniprotData["sequence"] != nm.base_sequence:
            nm.uniprot_new_seq = uniprotData["sequence"]

        if uniprotData["function"] != nm.function:
            nm.function = uniprotData["function"]
            nm.function_updated = date.today()

        nm.last_checked_uniprot = date.today()

        nm.save()


