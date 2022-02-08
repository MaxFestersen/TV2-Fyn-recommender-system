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
function checkCookieUserID(daysToExpire) {
    let uID = getCookie('user-id');
    let sID = sessionStorage.getItem('session-id');
    if (uID == null) {
        // If no user cookie is set, both user cookie and session id is set.
        setCookie("user-id", userID(), daysToExpire);
        sessionStorage.setItem("session-id", userID() + "-s");
        // Pushing user-id (deviceID) and session-id (sessionID) to database 
        $(document).ready(function(){
            var deviceID = getCookie('user-id');
            var sessionID = sessionStorage.getItem("session-id");
            var firstVisit = new Date().toISOString().split('T')[0];
            var screenWidth = screen.width;
            var screenHeight = screen.height;
            if(deviceID != "" && firstVisit != "" && screenWidth != "" && screenHeight != "" && sessionID != ""){
                $.ajax({
                    url: "php/device.php",
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
                        $.ajax({
                            url: "php/device_session.php",
                            type: "POST",
                            data: {
                                deviceID: deviceID,
                                sessionID: sessionID
                            },
                            cache: false,
                            succes: function(){
                                console.log(deviceID, sessionID);
                            }
                        })
                    }
                })
            }
        })
    }else if (sID == null){
        // Setting session-id (sessionID) if not set, and pushing session-id (sessionID) with user-id (deviceID) to database
        sessionStorage.setItem("session-id", userID() + "-s");
        $(document).ready(function(){
            var deviceID = getCookie('user-id');
            var sessionID = sessionStorage.getItem("session-id");
            if(deviceID != "" && sessionID != ""){
                $.ajax({
                    url: "php/device_session.php",
                    type: "POST",
                    data: {
                        deviceID: deviceID,
                        sessionID: sessionID
                    },
                    cache: false,
                    succes: function(){
                        console.log(deviceID, sessionID);
                    }
                })
            }
        })
    }
}

let daysToExpire = 30; // number of days before cookie expires
checkCookieUserID(daysToExpire);

/* Initiating variables to be updated */
let startDate = new Date();
let maxScroll = 0; 

/* Get user location */
/* Inspiration
	- https://www.w3schools.com/html/html5_geolocation.asp
	- https://tutorialmeta.com/question/javascript-pass-geolocation-as-string-variable
*/
function getLocation() {
	// Promise reults or serve rejection
    return new Promise((resolve, reject) => {
		// Check if geolocation is available
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition((position) => {
                return resolve(position);
            }, function(err) {
                return reject(err);
            });
        } else {
            return reject("Geolocation is not supported by this browser.");
        }
    })
}

/* Function for saving session info at first page load */
function saveSession(sessionID, date, elapsed, articleID, scrollY, lat, lon){
	if(sessionID != "" && date != "" && elapsed != "" && articleID != ""){
		$.ajax({
			url: "php/session.php",
			type: "POST",
			data: {
				sessionID: sessionID,
				date: date,
				elapsed: elapsed,
				articleID: articleID,
				scrollY: scrollY,
				lat: lat,
				lon: lon
			},
			cache: false,
			success: function(){
				console.log(sessionID, date, elapsed, articleID, scrollY, lat, lon);
			}
		})
	}
}

/* Function for updating session info at event */
function updateSession(scrollY){
    const sessionID = sessionStorage.getItem("session-id");
    const articleID = document.head.querySelector("[property='bazo:id'][content]").content;
    const endDate = new Date();
    const spentTime = endDate.getTime() - startDate.getTime();
    const elapsed = Math.floor(spentTime/1000);

	if(sessionID != "" && elapsed != "" && articleID != ""){
		$.ajax({
			url: "php/session_update.php",
			type: "POST",
			data: {
				sessionID: sessionID,
				elapsed: elapsed,
				articleID: articleID,
				scrollY: scrollY,
			},
			cache: false,
			success: function(){
				console.log(sessionID, elapsed, articleID, scrollY);
			}
		})
	}
    startDate = new Date(); // resetting start date after each update
}

/* Function for computing percentage of page scrolled */
function scrollPercentage() {
    var scrollPercentage = (((document.documentElement.scrollTop + document.body.scrollTop) / (document.documentElement.scrollHeight - document.documentElement.clientHeight) || 0) * 100);
    return scrollPercentage;
}

/* Pushing session info to database when page loads */
window.addEventListener('load', (event) => {
    const sessionID = sessionStorage.getItem("session-id");
    const date = new Date().toISOString().split('T')[0];
    const elapsed = 1; // can't be zero, so initial value is 1
    const articleID = document.head.querySelector("[property='bazo:id'][content]").content;
    const scrollY = maxScroll;

    (async function() {
        pos = await getLocation();
    })().then(() => {
        // If succes
        let lat = pos.coords.latitude.toFixed(3); // Get latitude and generalise position
        let lon = pos.coords.longitude.toFixed(3); // Get longitude and generalise position
        saveSession(sessionID, date, elapsed, articleID, scrollY, lat, lon);
    }).catch((err) => {
        // If failed
        console.error(err);
        let lat = "0,0"; 
        let lon = "0,0";
        saveSession(sessionID, date, elapsed, articleID, scrollY, lat, lon);
    })
});

/* Updating maxScroll whenever scrolling is happening,
and updating elapsed and scrollY in database */
document.addEventListener('scroll', function() {
    if(scrollPercentage() > maxScroll){
        maxScroll = Math.round(scrollPercentage());
    }
    scrollY = maxScroll;
	updateSession(scrollY);
});

/* Pushing updated elapsed time and scrollY to database, when switching tabs */
document.addEventListener('visibilitychange', function(){
    if (document.visibilityState === 'hidden') {
        scrollY = maxScroll;
		updateSession(scrollY);
    }
});

document.addEventListener('click', function(){
    scrollY = maxScroll;
    updateSession(scrollY);
})
