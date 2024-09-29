
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
        alert('The last query was not modified, loaded the next lastest reponse')
    }
    //count videos
    keyframe_to_video = {}
    video_grid = document.getElementById('videoGridResults')
    for (const [idx, frame_data] of jsonFile.entries()) {
        if (keyframe_to_video[frame_data['video']]==undefined){
            let newold = frame_data['video'].slice(-1)=='n'?'newkeyframe':'oldkeyframe'
            el = createElementFromHTML(`
                <div id="imgGridResults" class="gridcontainer ${newold}">
                    <h2 style='
                    width:100%; text-align:center; 
                    align-self:center; font-size: 2em;'>
                    ${frame_data['video']}</h2>
                </div>`)
            keyframe_to_video[frame_data['video']] = el
            video_grid.appendChild(el)
            video_grid.appendChild(createElementFromHTML(`<div class="hline"></div>)`))
        }
    }

    grid = document.getElementById('imgGridResults')
    for (const [idx, frame_data] of jsonFile.entries()) {
        //'let' not 'var': scope moment :D
        let htmlDOM = document.createElement('div')
        grid.appendChild(htmlDOM)
        // setTimeout(()=>{
        //     console.log('sd')
        // },5000)
        let htmlDOM2 = document.createElement('div')
        keyframe_to_video[frame_data['video']].append(htmlDOM2)
        let callback = (DOM_value)=>{
            htmlDOM.outerHTML = DOM_value.outerHTML
            htmlDOM2.outerHTML = DOM_value.outerHTML
        }
        get_DOM_from_index(frame_data['frame_index'],callback)
        // console.log('con cac')
    }
}

loadData()
loadPallete()
changeDisplayStyle()
changeDisplayStyle()

change_newold()
change_newold()
change_newold()

for (let i = 0; i < document.getElementsByTagName('textarea').length; i++){
    box = document.getElementsByTagName('textarea')[i]
    box.addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            e.preventDefault();
            form = document.getElementById('request')
            if (form['query_type'].value != 'text' && form['query_type'].value != 'texttext'
                && form['query_type'].value != 'text_ivs'
                && form['query_type'].value != 'text_ivt'
                && form['query_type'].value != 'texttext_ivt'
            ){
                form['query_type'].value = 'text'
            }
            submit(e);
        }
    })
}
document.getElementById('ocr-box').addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
        e.preventDefault();
        form = document.getElementById('request')
        form['query_type'].value = 'ocr'
        submit(e);
    }
})  
document.getElementById('url-textbox').addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
        e.preventDefault();
        form = document.getElementById('request')
        form['query_type'].value = 'url'
        submit(e);
    }
}) 

function changeDisplayStyle() {
    if (displayStyle=='keyframe'){
        displayStyle = 'video'
        document.getElementById('imgGridResults').style.display = 'none'
        document.getElementById('videoGridResults').style.display = 'block'
    } else {
        displayStyle = 'keyframe'
        document.getElementById('imgGridResults').style.display = 'grid'
        document.getElementById('videoGridResults').style.display = 'none'
    }
}
shortcut.add("CTRL+D", (event)=>{
    changeDisplayStyle()
});
shortcut.add("CTRL+1", function() {
    select_box = document.getElementById("query-type");
    changeSelected(select_box,'text')
});
shortcut.add("CTRL+2", function() {
    select_box = document.getElementById("query-type");
    changeSelected(select_box,'image')
});
shortcut.add("CTRL+3", function() {
    select_box = document.getElementById("query-type");
    changeSelected(select_box,'texttext')
});
shortcut.add("CTRL+4", function() {
    select_box = document.getElementById("query-type");
    changeSelected(select_box,'text_ivs')
});
shortcut.add("CTRL+5", function() {
    select_box = document.getElementById("query-type");
    changeSelected(select_box,'text_ivt')
});
document.addEventListener('keydown',(event)=>{
    if (event.key=='Escape'){
        closePopup()
    }
});

shortcut.add("F1", function() {
    alert("F1 pressed");
});

// url/text
function queryByIdx(idx){
    addParam("idx_query",idx)
    form = document.getElementById('request')
    form['query_type'].value = 'idx'
    submit()
}
function queryByIdxDinov2(idx){
    addParam("idx_query",idx)
    form = document.getElementById('request')
    form['query_type'].value = 'dinov2'
    submit()
}
async function beforeSubmit(eventObj) {
    addParam("last_displayStyle",displayStyle)
    addParam("last_newold",newold)
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
}
document.getElementById("request").addEventListener("submit", (eventObj)=>beforeSubmit(eventObj));

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

function bbox_submit(e, include_text=false){
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
    addParam("od_query",res)
    form = document.getElementById('request')
    form['query_type'].value = (include_text?'text_od':'od')
    submit(e)
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

function change_newold(){
    if (newold=='newkeyframe'){
        newold = 'oldkeyframe'
        els = document.getElementsByClassName('newkeyframe')
        for (let el of els){
            el.style.display = 'none'
        }
        els = document.getElementsByClassName('oldkeyframe')
        for (let el of els){
            el.style.display = (el.classList.contains('gridcontainer')?'grid':'block')
        }
    } else if (newold=='oldkeyframe') {
        newold = 'newold'
        els = document.getElementsByClassName('newkeyframe')
        for (let el of els){
            el.style.display = (el.classList.contains('gridcontainer')?'grid':'block')
        }
        els = document.getElementsByClassName('oldkeyframe')
        for (let el of els){
            el.style.display = (el.classList.contains('gridcontainer')?'grid':'block')
        }
    } else {
        newold = 'newkeyframe'
        els = document.getElementsByClassName('newkeyframe')
        for (let el of els){
            el.style.display = (el.classList.contains('gridcontainer')?'grid':'block')
        }
        els = document.getElementsByClassName('oldkeyframe')
        for (let el of els){
            el.style.display = 'none'
        }
    }
    document.getElementById('newold-text').innerText = newold
    return newold
}

async function autoSubmit(numSubmit, startPos){
    if (data_reponse&&data_reponse.length!=0){
        jsonFile = data_reponse
    } else {
        jsonFile = getJSON('data.json')
    }
    if (startPos >= jsonFile.length){
        return
    }
    jsonFile = jsonFile.slice(startPos,)
    let paramList = []
    for (let i = 0; i < numSubmit; i++){
        let kframe = jsonFile[i%jsonFile.length]['frame_index'];
        let submit = new XMLHttpRequest();
        var params = `idx=${kframe}&isKeyframe=true`
        paramList.push(params)
    }
    let cntSubmitted = 0
    let callback = function(){
        let params = paramList[cntSubmitted]
        let submit = new XMLHttpRequest();
        submit.open("POST", "/submit?" + params, true);
        submit.onreadystatechange = function() {
            if (submit.readyState == 4 && submit.status == 200) {
                cntSubmitted += 1
                toastr.success(`${cntSubmitted}/${numSubmit} saved`);
                if (cntSubmitted < numSubmit){
                    callback()
                }
            }
        }
        submit.send(null)
    }
    callback()
}


shortcut.add("CTRL+E", function() {
    let boxes = document.getElementsByTagName('textarea')
    for (let box of boxes){
        value = box.value
        value = value.replaceAll('\\','')
        value = value.replaceAll('/','')
        value = value.replaceAll('"','')
        value = value.replaceAll("'",'')
        if (value=='') continue
        value = translate(value)
        value = value.replaceAll('"','')
        value = value.replaceAll("'",'')
        box.value = value
    }
});
shortcut.add("ALT+Q", function() {
    let boxes = document.getElementsByTagName('textarea')
    boxes[0].focus()
});
shortcut.add("ALT+W", function() {
    let boxes = document.getElementsByTagName('textarea')
    boxes[1].focus()
});
shortcut.add("ALT+A", function() {
    let box = document.getElementById('ocr-box')
    box.focus()
});
shortcut.add("ALT+S", function() {
    let box = document.getElementById('num-clip-query')
    box.focus()
});
shortcut.add("CTRL+H", function() {
    change_newold()
});
shortcut.add("CTRL+S", async function() {
    let text = prompt("Enter number submit (num of frames, start pos[optional])", "10,0");
    if(text==null) return
    idx = text.indexOf(',')
    if (idx==-1){
        numSubmit = parseInt(text)
        startPos = 0
    } else {
        numSubmit = parseInt(text.slice(0,idx))
        startPos = parseInt(text.slice(idx+1))
    }
    autoSubmit(numSubmit, startPos)
})

function translate(text){
    var request = new XMLHttpRequest();
    var params = `text=${text}&dest=en&src=vi`
    request.open("GET", "translate?"+params, false);
    request.send(null)
    return request.responseText
}

document.getElementById("num-show-query").addEventListener("change", function() { 
    show = document.getElementById("num-show-query")
    clip = document.getElementById("num-clip-query")
    clip.value = Math.max(clip.value,show.value)
});

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
function addParam(key, value){
    form = document.getElementById('request')
    input = document.createElement("input");
    input.type = "hidden";
    input.name = key;
    input.value = value;
    form.appendChild(input);
}
function submit(e){
    form = document.getElementById('request')
    beforeSubmit(e)
    form.submit()
}

window.queryByIdxDinov2 = queryByIdxDinov2
window.queryByIdx = queryByIdx