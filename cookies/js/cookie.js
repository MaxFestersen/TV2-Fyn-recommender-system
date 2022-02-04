cookieEnd =  ' path=/; max-age=3600'
document.cookie = 'name=device-information;' + cookieEnd;

/* function for setting cookies*/
function setCookie(name,value,days) {
    var expires = "";
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days*24*60*60*1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + (value || "")  + expires + "; path=/";
}

/* userID is a string that consists of number of miliseconds since 1/1-1970 and a random 3 character integer */

function userID() {
    var date = Date.now()
    var random = Math.floor(Math.random() * 1000)
    return date + "-" + random
}

/* function for getting cookie value, returns null if none set for a name*/ 
function getCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for(var i=0;i < ca.length;i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') c = c.substring(1,c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
    }
    return null;
}

/* function for checking if user-id is set, and if not sets it*/
function checkCookieUserID() {
    let id = getCookie('user-id');
    if (id == null) {
        setCookie("user-id",userID(),30);
    }
}

checkCookieUserID();
console.log(document.cookie);

/* Get user location */
let lat = "";
let lon = "";
function getLocation() {
	if (navigator.geolocation) {
		navigator.geolocation.getCurrentPosition(getPosition);
	} else {
		lat = false;
		lon = false;
	}
}

function getPosition(position) {
	lat = position.coords.latitude;
	lon = position.coords.longitude;
}

getLocation();
/* code if successful */
/* Update not working due to functions running last on load) */
/*
latString = 'lat=' + lat + ';';
lonString = 'lon=' + lon + ';';
document.cookie = latString + cookieEnd;
document.cookie = lonString + cookieEnd;
console.log(document.cookie);
*/
