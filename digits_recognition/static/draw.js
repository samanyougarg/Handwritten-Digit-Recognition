var drawing = false;

var context;

var offset_left = 0;
var offset_top = 0;


function start_canvas ()
{
    var scribbler = document.getElementById ("the_stage");
    context = scribbler.getContext ("2d");
    scribbler.onmousedown = function (event) {mousedown(event)};
    scribbler.onmousemove = function (event) {mousemove(event)};
    scribbler.onmouseup   = function (event) {mouseup(event)};
    for (var o = scribbler; o ; o = o.offsetParent) {
    offset_left += (o.offsetLeft - o.scrollLeft);
    offset_top  += (o.offsetTop - o.scrollTop);
    }
    draw();
}

function getPosition(evt)
{
    evt = (evt) ?  evt : ((event) ? event : null);
    var left = 0;
    var top = 0;
    var scribbler = document.getElementById("the_stage");

    if (evt.pageX) {
    left = evt.pageX;
    top  = evt.pageY;
    } else if (document.documentElement.scrollLeft) {
    left = evt.clientX + document.documentElement.scrollLeft;
    top  = evt.clientY + document.documentElement.scrollTop;
    } else  {
    left = evt.clientX + document.body.scrollLeft;
    top  = evt.clientY + document.body.scrollTop;
    }
    left -= offset_left;
    top -= offset_top;

    return {x : left, y : top}; 
}

function
mousedown(event)
{
    drawing = true;
    var location = getPosition(event);
    context.lineWidth = 20.0;
    context.strokeStyle="#000000";
    context.beginPath();
    context.moveTo(location.x,location.y);
}


function
mousemove(event)
{
    if (!drawing) 
        return;
    var location = getPosition(event);
    context.lineTo(location.x,location.y);
    context.stroke();
}



function
mouseup(event)
{
    if (!drawing) 
        return;
    mousemove(event);
    drawing = false;
}

function draw()
{

    context.fillStyle = '#ffffff';
    context.fillRect(0, 0, 350, 350);

}

function clearCanvas()
{
    context.clearRect (0, 0, 350, 350);
    draw();
    document.getElementById("rec_result").innerHTML = "";
}


function processImg()
{
    document.getElementById("rec_result").innerHTML = "Wait...";
    
    var scribbler = document.getElementById ("the_stage");
    var imageData =  scribbler.toDataURL('image/png');
    var dataTemp = imageData.substr(22);  

    var sendPackage = {"id": "1", "txt": dataTemp};
    $.post("/process", sendPackage, function(data){
        data = JSON.parse(data);
        if(data["status"] == 1)
        {
            document.getElementById("rec_result").innerHTML = data["result"];
        }
        else
        {
            document.getElementById("rec_result").innerHTML = "failed";
        }
    });
}

onload = start_canvas;