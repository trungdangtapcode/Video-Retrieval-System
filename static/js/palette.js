// Add dragstart event listeners to palettes

function allowDrop(ev) {
    ev.preventDefault();
}

function drag(ev) {
    console.log('hi')
    ev.dataTransfer.setData("text", ev.target.id);
}

function drop(ev) {
    ev.preventDefault();
    var data = ev.dataTransfer.getData("text");
    ev.target.appendChild(document.getElementById(data));
    console.log()
}

