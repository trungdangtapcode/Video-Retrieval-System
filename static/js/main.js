
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
    console.log(jsonFile)
    grid = document.getElementById('imgGridResults')
    for (const [idx, frame_data] of jsonFile.entries()) {
        htmlDOM = get_DOM_from_index(frame_data['frame_index'])
        grid.appendChild(htmlDOM)
    }
}

loadData()

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
}

function dropPalette(ev) {
    ev.preventDefault();
    // var data = ev.dataTransfer.getData("text");
    // const clone = document.getElementById(data);
    var palette = draggedItem;
    if (!draggedItem.hasAttribute("copied")){
        palette = draggedItem.cloneNode(true);
    }
    if (palette.className!="dragbox"){
        return;
    }
    palette.style.position = 'absolute';
    whiteboard.appendChild(palette);
    //palette.size wont update until append  
    // palette.style.left = `${ev.clientX-palette.clientWidth/2}px`;
    // palette.style.top = `${ev.clientY-palette.clientHeight/2}px`;
    palette.style.left = `${ev.clientX-x_diff}px`;
    palette.style.top = `${ev.clientY-y_diff}px`;
    palette.setAttribute("copied",'');
    palette.childNodes[1].removeAttribute('hidden')
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

}