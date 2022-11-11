window.onload =  function(){

    var autocompleteElements = document.getElementsByClassName("select2 select2-container select2-container--default");
    for(var i=0; i<autocompleteElements.length; i++){
        autocompleteElements[i].classList.add("d-none");
    }
}

