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

function getOS() {
    var OSName = "Unknown OS";
    if (navigator.userAgent.indexOf("Win") != -1) OSName = "Windows";
    if (navigator.userAgent.indexOf("Mac") != -1) OSName = "Macintosh";
    if (navigator.userAgent.indexOf("Linux") != -1) OSName = "Linux";
    if (navigator.userAgent.indexOf("Android") != -1) OSName = "Android";
    if (navigator.userAgent.indexOf("like Mac") != -1) OSName = "iOS";
    return OSName;
}

function getBrowser() {
	// inspired by https://codepedia.info/detect-browser-in-javascript
	var browserName = (function (agent) {
		switch(true) {
            case agent.indexOf("edge") > -1: return "MS Edge";
            case agent.indexOf("edg/") > -1: return "Edge ( chromium based)";
            case agent.indexOf("opr") > -1 && !!window.opr: return "Opera";
            case agent.indexOf("chrome") > -1 && !!window.chrome: return "Chrome";
            case agent.indexOf("trident") > -1: return "MS IE";
            case agent.indexOf("firefox") > -1: return "Mozilla Firefox";
            case agent.indexOf("safari") > -1: return "Safari";
            default: return "other";
        }
    })(window.navigator.userAgent.toLowerCase());
	return(browserName)
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
		var deviceID = getCookie('user-id');
		var sessionID = sessionStorage.getItem("session-id");
		var firstVisit = new Date().toISOString().split('T')[0];
		var screenWidth = screen.width;
		var screenHeight = screen.height;
		var deviceOS = getOS();
		var deviceVendor = getBrowser()
		if(deviceID != "" && firstVisit != "" && screenWidth != "" && screenHeight != "" && sessionID != ""){
			let xhttp = new XMLHttpRequest();
			xhttp.open("POST", fullUrl + "php/device.php", true);
			xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
			let data = `deviceID=${deviceID}&firstVisit=${firstVisit}&screenWidth=${screenWidth}&screenHeight=${screenHeight}&deviceOS=${deviceOS}&deviceVendor=${deviceVendor}`;
			data = data.replace( /%20/g, '+' );
			console.log(data);
		
			// Define what happens on successful data submission
			xhttp.addEventListener( 'load', function(event) {
				console.log('checkCookieUserID succes');
				console.log(deviceID, firstVisit, screenHeight, screenWidth, deviceOS);
			});

			// Define what happens in case of error
			xhttp.addEventListener( 'error', function(event) {
				console.log('checkCookieUserID error');
				console.log(xhttp.responseText);
			});

			xhttp.send(data);
			
			let xhttp2 = new XMLHttpRequest();
			xhttp2.open("POST", fullUrl + "php/session.php", true);
			xhttp2.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
			let data2 = `deviceID=${deviceID}&sessionID=${sessionID}`;
			data2 = data2.replace( /%20/g, '+' );
			console.log(data2);
			
			xhttp2.addEventListener( 'load', function(event) {
				console.log('checkCookieUserID second succes');
				console.log(deviceID, sessionID);
			});
			
			// Define what happens in case of error
			xhttp2.addEventListener( 'error', function(event) {
				console.log('checkCookieUserID second error');
				console.log(xhttp2.responseText);
			});
			
			xhttp2.send(data2);
			/*$.ajax({
				url: fullUrl + "php/device.php",
				type: "POST",
				data: {
					deviceID: deviceID,
					firstVisit: firstVisit,
					screenWidth: screenWidth,
					screenHeight: screenHeight,
					deviceOS: deviceOS,
					deviceVendor: deviceVendor
				},
				cache: false,
				success: function(){
					console.log(deviceID, firstVisit, screenHeight, screenWidth, deviceOS);
					$.ajax({
						url: fullUrl + "php/session.php",
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
			})*/
		}
    } else if (sID == null){
        // Setting session-id (sessionID) if not set, and pushing session-id (sessionID) with user-id (deviceID) to database
        sessionStorage.setItem("session-id", userID() + "-s");
        //$(document).ready(function(){
		var deviceID = getCookie('user-id');
		var sessionID = sessionStorage.getItem("session-id");
		if(deviceID != "" && sessionID != ""){
			let xhttp = new XMLHttpRequest();
			xhttp.open("POST", fullUrl + "php/session.php", true);
			xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
			let data = `deviceID=${deviceID}&sessionID=${sessionID}`;
			data = data.replace( /%20/g, '+' );
			console.log(data);

			xhttp.addEventListener( 'load', function(event) {
				console.log('checkCookieUserID else succes');
				console.log(deviceID, sessionID);
			});
			
			// Define what happens in case of error
			xhttp.addEventListener( 'error', function(event) {
				console.log('checkCookieUserID else error');
				console.log(xhttp2.responseText);
			});
			
			xhttp.send(data);
			/*$.ajax({
				url: fullUrl + "php/session.php",
				type: "POST",
				data: {
					deviceID: deviceID,
					sessionID: sessionID
				},
				cache: false,
				succes: function(){
					console.log(deviceID, sessionID);
				}
			})*/
		}
    }
}
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
		let xhttp = new XMLHttpRequest();
		
		// Define what happens on successful data submission
		xhttp.addEventListener( 'load', function(event) {
			console.log('saveSession succes');
		});

		// Define what happens in case of error
		xhttp.addEventListener( 'error', function(event) {
			console.log('saveSession error');
			console.log(xhttp.responseText);
		});
		
		xhttp.open("POST", fullUrl + "php/sessionInfo.php", true);
		xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
		let data = `sessionID=${sessionID}&date=${date}&elapsed=${elapsed}&articleID=${articleID}&scrollY=${scrollY}&lat=${lat}&lon=${lon}`;
		data = data.replace( /%20/g, '+' );
		console.log(data);
		/*xhttp.onreadystatechange = function() {
			// Tilsvarende succes
			console.log(sessionID, date, elapsed, articleID, scrollY, lat, lon);
			console.log(xhttp.responseText);
			
		};*/
		xhttp.send(data);
		/*$.ajax({
			url: fullUrl + "php/sessionInfo.php",
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
		})*/
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
		let xhttp = new XMLHttpRequest();
		xhttp.open("POST", fullUrl + "php/sessionInfo_update.php", true);
		xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
		let data = `sessionID=${sessionID}&elapsed=${elapsed}&articleID=${articleID}&scrollY=${scrollY}`;
		data = data.replace( /%20/g, '+' );
		console.log(data);
		
		// Define what happens on successful data submission
		xhttp.addEventListener( 'load', function(event) {
			console.log('updateSession succes');
		});

		// Define what happens in case of error
		xhttp.addEventListener( 'error', function(event) {
			console.log('updateSession error');
			console.log(xhttp.responseText);
		});

		/*xhttp.onreadystatechange = function() {
			// Tilsvarende succes
			console.log(sessionID, elapsed, articleID, scrollY);
			console.log(xhttp.responseText);
		}*/
		xhttp.send(data);
		/*$.ajax({
			url: fullUrl + "php/sessionInfo_update.php",
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
		})*/
	}
    startDate = new Date(); // resetting start date after each update
}

/* Function for computing percentage of page scrolled */
function scrollPercentage() {
    var scrollPercentage = (((document.documentElement.scrollTop + document.body.scrollTop) / (document.documentElement.scrollHeight - document.documentElement.clientHeight) || 0) * 100);
    return scrollPercentage;
}

// path of cookie scripts
var script = document.currentScript;
var fullUrl = script.src.split('/').slice(0, -2).join('/')+'/';

/* Pushing session info to database when page loads */
window.addEventListener('load', (event) => {
	let daysToExpire = 30; // number of days before cookie expires

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
	/* Initiating variables to be updated */
	startDate = new Date();
	let maxScroll = 0; 
	
	const sessionID = sessionStorage.getItem("session-id");
	const date = new Date().toISOString().split('T')[0];
	const elapsed = 1; // can't be zero, so initial value is 1
	const articleID = document.head.querySelector("[property='bazo:id'][content]").content;
	let scrollY = maxScroll;

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
});

