
function getJSON(filename){
    var request = new XMLHttpRequest();
    request.open("GET", "concac/reponse/data.json", false);
    request.send(null)
    var my_JSON_object = JSON.parse(request.responseText);
    return my_JSON_object
}

function get_DOM_from_index(image_index, callback){
    var request = new XMLHttpRequest();
    // request.open("GET", "thumbnail_template/" + image_index, false);
    request.open("GET", "thumbnail_template/" + image_index, true);
    request.send(null)
    request.onreadystatechange = function() {
        if (request.readyState == 4 && request.status == 200) {
            callback(createElementFromHTML(request.responseText))
        }
    }
    // return createElementFromHTML(request.responseText)
}

function createElementFromHTML(htmlString) {
    var div = document.createElement('div');
    div.innerHTML = htmlString.trim();
  
    // Change this to div.childNodes to support multiple top-level nodes.
    return div.firstChild;
  }

  function loadData(){
    if (data_reponse&&data_reponse.length!=0){
        jsonFile = data_reponse
    } else {
        jsonFile = getJSON('data.json')
    }
    grid = document.getElementById('imgGridResults')
    for (const [idx, frame_data] of jsonFile.entries()) {
        //'let' not 'var': scope moment :D
        let htmlDOM = document.createElement('div')
        grid.appendChild(htmlDOM)
        // setTimeout(()=>{
        //     console.log('sd')
        // },5000)
        let callback = (DOM_value)=>{
            htmlDOM.outerHTML = DOM_value.outerHTML
        }
        get_DOM_from_index(frame_data['frame_index'],callback)
        // console.log('con cac')
    }
}

loadData()
loadPallete()

// url/text
function queryByIdx(idx){
    form = document.getElementById('request')
    input = document.createElement("input");
    input.type = "hidden";
    input.name = "idx_query";
    input.value = idx;
    form['query_type'].value = 'idx'
    form.appendChild(input);
    form.submit()
}
function queryByIdxDinov2(idx){
    form = document.getElementById('request')
    input = document.createElement("input");
    input.type = "hidden";
    input.name = "idx_query";
    input.value = idx;
    form['query_type'].value = 'dinov2'
    form.appendChild(input);
    form.submit()
}

document.getElementById("request").addEventListener("submit", async function(eventObj) {
    form = document.getElementById('request')
    select_box = document.getElementById("query-type");
    if (select_box.value=='image'){
        image = document.getElementById("image-file").files[0]
        if (image==null){
            alert('Please select an image')
            eventObj.preventDefault();
            return false;
        }
        let formData = new FormData();
        formData.append("image", image);
        formData.append("model_name", form['model_name'].value);
        await fetch('/upload_image', {method: "POST", 
            body: formData});
        // alert('Image uploaded successfully')
        eventObj.preventDefault(); //preven not working
        return false
    }
    if (select_box.value=='url'&&
        !isValidUrl(document.getElementById("url-textbox").value)){
        alert('Please enter a valid URL')
        eventObj.preventDefault();
        return false
    }
    // if (queryType!=null){
    //     // eventObj.preventDefault();
    //     var input = document.createElement("input");
    //     input.type = "hidden";
    //     input.name = "queryType";
    //     input.value = queryType;
    //     this.appendChild(input);
    // }
    return true;
});

function allowDrop(ev) {
    ev.preventDefault();
}

x_diff = 0
y_diff = 0
draggedItem = null;
whiteboard = document.getElementById("whiteboard");
num2char = ['a','b','c','d','e','f','g','h']

function dragPalette(ev) {
    ev.dataTransfer.setData("text", ev.target.id);
    draggedItem = ev.target.parentElement;
    var rect = draggedItem.getBoundingClientRect();
    x_diff = ev.clientX-rect.left;
    y_diff = ev.clientY-rect.top;
    window.scrollTo(0, 0); 
}

function dropPalette(ev) {
    defaultPaletteBox = window.defaultPaletteBox
    //>draggedItem -> whiteboard
    ev.preventDefault();
    var palette = draggedItem;
    if (!draggedItem.hasAttribute("copied")){
        palette = draggedItem.cloneNode(true);
    }
    if (palette.className!="dragbox"){
        return;
    }
    palette.style.position = 'absolute';
    whiteboard.appendChild(palette);

    //>set postision and size
    //palette.size wont update until append  
    palette.style.left = `${ev.clientX-x_diff}px`;
    palette.style.top = `${ev.clientY-y_diff}px`;
    // let box = palette.getBoundingClientRect() => not work because not render
    //client > offset (include border)
    //cant assign value for right/bottom
    if (!palette.hasAttribute("copied")){
        palette.style.width = `${defaultPaletteBox.clientWidth}px`;
        palette.style.height = `${defaultPaletteBox.clientHeight}px`;
    }

    //>set attribute
    palette.setAttribute("copied",'');
    palette.childNodes[0].removeAttribute('hidden')
    // IF ON WATAME AND XI: palette.childNodes[1].removeAttribute('hidden')
    palette.style.resize = 'both'
}

function bbox_submit(){
    var boxes = whiteboard.childNodes;
    res = ''
    for(var i=0, len = whiteboard.childElementCount ; i < len; ++i){
        bbox = boxes[i];
        rect = bbox.getBoundingClientRect()
        wb = whiteboard.getBoundingClientRect()
        x = (rect.left-wb.left)/wb.width
        y = (rect.top-wb.top)/wb.height
        u = (rect.right-wb.left)/wb.width
        v = (rect.bottom-wb.top)/wb.height
        for (var nx = 0; nx < 8; nx++) for (var ny = 0; ny < 8; ny++){
        bx = nx/8
        by = ny/8
        bu = (nx+1)/8
        bv = (ny+1)/8
        if (!(x<bu&&y<bv&&u>bx&&v>by)) continue;
        // console.log(nx,ny,bbox.getAttribute('palette_name'))
        res += `${nx+1}${num2char[ny]}_${bbox.getAttribute('palette_name')} `
        }
    }
    console.log(res)
    return res

}
// window.bbox_submit = bbox_submit

// FACK GLOBAL: window.defaultPaletteBox = document.getElementsByClassName("dragbox")[0];
function loadPallete(){
    var palette_list = ['person','man','woman','human_face','musical_instrument','sports','skateboard','glasses','bicycle','motorcycle','car','truck','boat','parachute','airplane','bench','chair','sofa','building','umbrella','wine_glass','cup','dessert','cell_phone','television','laptop_computer','book','cat','dog','horse','bird','flower','tree']
    palette_place = document.getElementById('palette-place')
    for (const [_,palette_name] of palette_list.entries()){
        let palette = document.createElement('div')
        palette.className = 'dragbox'
        palette.setAttribute('palette_name',palette_name)
        palette.innerHTML = ''
        palette.innerHTML += `<span id="close-btn" class="close-btn" onclick="this.parentElement.remove()" hidden="">×</span>`
        palette.innerHTML += `<img draggable="true" ondragstart="dragPalette(event)" width="100%" height="100%" id="palette-img" src="concac/palette/${palette_name}.png">`
        palette_place.appendChild(palette)
    }
    window.defaultPaletteBox = document.getElementsByClassName("dragbox")[2]
}


const isValidUrl = urlString=> {
    var urlPattern = new RegExp('^(https?:\\/\\/)?'+ // validate protocol
  '((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.)+[a-z]{2,}|'+ // validate domain name
  '((\\d{1,3}\\.){3}\\d{1,3}))'+ // validate OR ip (v4) address
  '(\\:\\d+)?(\\/[-a-z\\d%_.~+]*)*'+ // validate port and path
  '(\\?[;&a-z\\d%_.~+=-]*)?'+ // validate query string
  '(\\#[-a-z\\d_]*)?$','i'); // validate fragment locator
    if (!urlPattern.test(urlString)){
        console.log('URL cant match pattern, try parse')
        // return false;
    }
    let url;
    try {
        url = new URL(urlString);
    } catch (_) {
        console.log('URL cant parse')
        return false;  
    }

    return url.protocol === "http:" || url.protocol === "https:";
}