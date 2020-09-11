//// For protein detail view: Highlight sequence for current page and base sequence ////
var idTitle = document.getElementsByClassName("msaIdCatcher");
id = idTitle[0].innerHTML;
id = id.replace("Protein Record #", "");

//Get protein_names from table headers
proteinnameElements = document.getElementsByClassName("msaProtNameCatcher")
//Get table rows
var sequenceidrowElements = document.getElementsByClassName("sequenceidrow");

//Loop through table rows
for (var i = 0; i < sequenceidrowElements.length; i++) {

    //Get sequence id
    var sequenceidElement = sequenceidrowElements[i].getElementsByClassName("sequenceid");
    idElement = sequenceidElement[0].innerHTML

    //Check if ID is ID from page heading
    if (idElement == id) {

        //Get sequence element and change colour of ID and sequence elemnt
        var alignsequenceElement = sequenceidrowElements[i].getElementsByClassName("alignsequence");
        sequenceidElement[0].style.color = "#b80090";
        alignsequenceElement[0].style.color = "#b80090";
    }

    //Loop through protein names in table headers and Check if ID in table matches protein name
    //Then change colour of ID and sequence
        for (var j = 0; j < proteinnameElements.length; j++){
            let proteinname = proteinnameElements[j].innerHTML
            if (idElement == proteinname) {
                var alignsequenceElement = sequenceidrowElements[i].getElementsByClassName("alignsequence");
                sequenceidElement[0].style.color = "red";
                alignsequenceElement[0].style.color = "red";
            }
        }
}


////