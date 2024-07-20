
function getJSON(filename){
    var request = new XMLHttpRequest();
    request.open("GET", "concac/reponse/data.json", false);
    request.send(null)
    var my_JSON_object = JSON.parse(request.responseText);
    return my_JSON_object
}

function get_DOM_from_index(image_index){
    var request = new XMLHttpRequest();
    request.open("GET", "thumbnail_template/" + image_index, false);
    request.send(null)
    return createElementFromHTML(request.responseText)
}

function createElementFromHTML(htmlString) {
    var div = document.createElement('div');
    div.innerHTML = htmlString.trim();
  
    // Change this to div.childNodes to support multiple top-level nodes.
    return div.firstChild;
  }

function loadData(){
    jsonFile = getJSON('data.json');
    grid = document.getElementById('imgGridResults')
    for (const [idx, frame_data] of jsonFile.entries()) {
        htmlDOM = get_DOM_from_index(frame_data['frame_index'])
        grid.appendChild(htmlDOM)
    }
}

loadData()