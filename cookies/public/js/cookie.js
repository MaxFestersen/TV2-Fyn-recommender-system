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
let daysToExpire = 30; // number of days before cookie expires

function checkCookieUserID() {
    let id = getCookie('user-id');
    if (id == null) {
        setCookie("user-id", userID(), daysToExpire);

        $(document).ready(function(){
            var deviceID = getCookie('user-id');
            var firstVisit = new Date().toISOString().split('T')[0];
            var screenWidth = screen.width;
            var screenHeight = screen.height;
            if(deviceID != "" && firstVisit != "" && screenWidth != "" && screenHeight != ""){
                $.ajax({
                    url: "/php/save.php",
                    type: "POST",
                    data: {
                        deviceID: deviceID,
                        firstVisit: firstVisit,
                        screenWidth: screenWidth,
                        screenHeight: screenHeight
                    },
                    cache: false,
                    success: function(){
                        console.log(deviceID, firstVisit, screenHeight, screenWidth);
                    }
                })
            }
        })
    }
}

checkCookieUserID();

/* some variables for session db
var deviceID = getCookie('user-id');
var date = new Date().toISOString().split('T')[0];
var elapsed = some kind of timer
var articleID = document.head.querySelector("[property='bazo:id'][content]").content;
*/


/* Get user location */

/* let lat = "";
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

getLocation(); */

/* code if successful */
/* Update not working due to functions running last on load) */
/*
latString = 'lat=' + lat + ';';
lonString = 'lon=' + lon + ';';
document.cookie = latString + cookieEnd;
document.cookie = lonString + cookieEnd;
console.log(document.cookie);
*/
