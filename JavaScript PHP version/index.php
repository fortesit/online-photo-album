<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Photo Album</title>
<style>
	
	.show-image {
	    position: relative;
	    float:left;
	    display: inline;
	}
	
	.edit {
		position: absolute;
		top: 2px;
		right: 30px;
		display: none;
	}
	
	.delete {
		position: absolute;
		top: 2px;
		right: 5px;
		display: none;
	}
</style>
</head>

<body>
Auto update: <input id="auto_update" type="button" name="on" value="on" onclick="switch_auto_update()">
<div id="display"> <table id="display_table" border=0> </table></div>
<div id="error_msg" style="color:#ff0000"> </div>
<div id="dropbox" style="width:100%; height:30px; border:solid 1px;"> <div id="drop_text"> Drop file here... </div> <progress id="upload_progress" value="0" max="100" hidden> </div>

<script language ="javascript" type="text/javascript">
var filename;
var interval_id;
var height;
var width;

function switch_auto_update() {
	var auto_update = document.getElementById("auto_update");
	if (auto_update.value == "on") {
		auto_update.name = "off";
		auto_update.value = "off";
		clearInterval(interval_id);
	} else {
		auto_update.name = "on";
		auto_update.value = "on";
		interval_id = setInterval(function(){update_display()}, 5000);
	}
}

function image_mouseover(e) {
	var img = document.getElementById(e.currentTarget.id);
	var edit_button = document.querySelector('#' + e.currentTarget.id + ' .edit');
	var delete_button = document.querySelector('#' + e.currentTarget.id + ' .delete');
	edit_button.style.display = "block";
	delete_button.style.display = "block";
	img.style.border="2px solid red";
}

function image_mouseout(e) {
	var img = document.getElementById(e.currentTarget.id);
	var edit_button = document.querySelector('#' + e.currentTarget.id + ' .edit');
	var delete_button = document.querySelector('#' + e.currentTarget.id + ' .delete');
	edit_button.style.display = "none";
	delete_button.style.display = "none";
	img.style.border="0px";
}

function edit_description(e) {
	var description = window.prompt("Please enter the description within 50 characters");
	
	description = description.replace(/&/g, "&amp;");
	description = description.replace(/</g, "&lt;");
	description = description.replace(/>/g, "&gt;");
	description = description.replace(/"/g, "&quot;");
	description = description.replace(/'/g, "&#39;");
	
	if (description.length > 50) {
		alert("You cannot input more than 50 characters for the description");
	} else {
		var file_name = document.getElementById(e.currentTarget.id).id;
		file_name = file_name.substring(5);
		
		var xhr = new XMLHttpRequest();
		xhr.open('POST', 'update.php', true);
		xhr.setRequestHeader('FILE_NAME', file_name);
		xhr.setRequestHeader('DESCRIPTION', description);
		xhr.send(null);
	}
}

function delete_photo(e) {
	answer = window.confirm("Do you really want to delete this photo?");
	if (answer) {
		var file_name = document.getElementById(e.currentTarget.id).id;
		file_name = file_name.substring(4);
		
		var xhr = new XMLHttpRequest();
		xhr.open('POST', 'update.php', true);
		xhr.setRequestHeader('FILE_NAME', file_name);
		xhr.setRequestHeader('DELETE', answer);
		xhr.send(null);
	}
}

function img_clicked(e) {

	var bg_grey = document.createElement("div");
	bg_grey.setAttribute("id", "background");
	bg_grey.setAttribute("style", "background-color:#808080; opacity: 0.5; position: fixed; top: 0px; left: 0px; z-index: 10; height: 100%; width: 100%; display: block;");
	bg_grey.setAttribute("onclick", "remove_bg(event)");
	document.body.appendChild(bg_grey);
	
	var big_img_div = document.createElement("div");
	big_img_div.setAttribute("id", "big_img_div");
	big_img_div.setAttribute("style", "position: absolute; top:50%; left:50%; -webkit-transform: translate(-50%, -50%); z-index:20; cursor: move;");
	big_img_div.setAttribute("draggable", "true");
	document.body.appendChild(big_img_div);
	
	var big_img = document.createElement("img");
	big_img.setAttribute("id", "big_img");
	big_img.setAttribute("src", "img/" + e.currentTarget.id);
	big_img_div.appendChild(big_img);
	
	big_img.addEventListener('load', function(){
		new_big_img = big_img;
		var height = big_img.height;
		var width = big_img.width;
		if (height > window.innerHeight * 0.7 && width > window.innerWidth * 0.7) {
			if (width/(height/(window.innerHeight * 0.7)) > (width/(window.innerWidth * 0.7))) {
				new_big_img.setAttribute("width", window.innerWidth * 0.7);
			} else {
				new_big_img.setAttribute("height", window.innerHeight * 0.7);
			}
		} else {
			if (width > window.innerWidth * 0.7) {
				new_big_img.setAttribute("width", window.innerWidth * 0.7);
			} else if (height > window.innerHeight * 0.7) {
				new_big_img.setAttribute("height", window.innerHeight * 0.7);
			}
		}
		big_img_div.removeChild(big_img);
		big_img_div.appendChild(new_big_img);
	}, false);
	
	big_img_div.addEventListener("mousedown", downHandler, false);
	
}

function downHandler(e) {
	e.preventDefault();
	e.stopPropagation();
	
	diffX = e.clientX - big_img_div.offsetLeft;
	diffY = e.clientY - big_img_div.offsetTop;
	
	big_img_div.addEventListener("mouseup", upHandler, false);
	big_img_div.addEventListener("mousemove", moveHandler, false);
}

function upHandler(e) {
	e.preventDefault();
	e.stopPropagation();

	big_img_div.removeEventListener("mouseup", upHandler, false);
	big_img_div.removeEventListener("mousemove", moveHandler, false);
}

function moveHandler(e) {
	e.preventDefault();
	e.stopPropagation();

	big_img_div.style.left = new String(e.clientX - diffX) + "px";
	big_img_div.style.top = new String(e.clientY - diffY) + "px";
}

function remove_bg(e) {
	var bg_grey = document.getElementById(e.currentTarget.id);
	document.body.removeChild(bg_grey);
	document.body.removeChild(big_img_div);
}

function update_display() {
	var layout = document.getElementById("display_table");
	var xhr = new XMLHttpRequest();
	xhr.open('POST', 'upload.php', true);
	xhr.onreadystatechange = function () {
	    if(xhr.readyState == 4)
	    {
	    	if(xhr.status == 200) {
	   	    	var result = xhr.responseText;
		        var json = JSON.parse(result);
		        var file_count = json["file_count"];
		        var html_code = '';
		        for (i=0; i<file_count; i++) {
		        	if (i%4 == 0) {
			        	html_code = html_code + "<tr height=100>";
		        	}
		        	html_code = html_code + "<td width=200><div class=\"show-image\" id=\"div" + i + "\" onmouseover=\"image_mouseover(event)\" onmouseout=\"image_mouseout(event)\"><img id=\"" + json["files"][i]["filename"] + "\" src=\"img/thumbnail/" + json["files"][i]["filename"] + "\" title=\"" + json["files"][i]["description"] + "\" onclick=\"img_clicked(event)\" ><button id=\"" + "edit_" + json["files"][i]["filename"] + "\" class=\"edit\" onclick=\"edit_description(event)\">&#9998;</button><button id=\"" + "del_" + json["files"][i]["filename"] + "\" class=\"delete\" onclick=\"delete_photo(event)\">&#10005;</button></div></td>";
			        if (i%4 == 3) {
			        	html_code = html_code + "</tr>";
		        	}
		        }
		        if (i%4 != 3) {
		        	html_code = html_code + "</tr>";
	        	}
	        	layout.innerHTML = html_code;
	    	}
	    }
	};
	xhr.send(null);
}

function handleReaderLoadEnd(e) {
	bar = document.getElementById("upload_progress");
	drop_text = document.getElementById("drop_text");

	// get the image data
	var data = e.target.result.split(',')[1];
	
	var xhr = new XMLHttpRequest();
	xhr.open('POST', 'upload.php', true);
	xhr.setRequestHeader('FILE_NAME', filename);
	
	/* Bind a progress event */
	xhr.upload.addEventListener('progress', function(e){
		var percent = e.loaded / e.total * 100;
		bar.value = percent;
		bar.style.display = "block";
		drop_text.style.display = "none";
	}, false);
	
	/* Bind a loadend event */
	xhr.upload.addEventListener('loadend', function(e){
		xhr.onreadystatechange = function () {
		    if(xhr.readyState == 4)
		    {
		    	if(xhr.status == 200) {
			    	var result = xhr.responseText;
			        var json = JSON.parse(result);
			        error_msg = document.getElementById("error_msg");
			        error_msg.innerHTML = json["error_msg"];
			        bar.style.display = "none";
					drop_text.style.display = "block";
		    	}
		    }
		};
	}, false);
	
	/* You still need to add something here */

	xhr.send(data);
}

function init() {
	var dropbox = document.getElementById("dropbox");
	dropbox.addEventListener("dragover", function(e) {
		e.stopPropagation();
		e.preventDefault();
	}, false);
	
	dropbox.addEventListener("drop", function(e) {
		e.stopPropagation();
		e.preventDefault();
		var file = e.dataTransfer.files[0];
		filename = file.name;
		
		/* You still need to add something here */
	
		var reader = new FileReader();
		// init the reader event handlers
		reader.onloadend = handleReaderLoadEnd;
		// begin the read operation
		reader.readAsDataURL(file);
	}, false);
	update_display();
	interval_id = setInterval(function(){update_display()}, 5000);
}

window.addEventListener("load", init, false);

</script>
</body>
</html>