/* function for setting cookies*/
function setCookie(name,value,days) {
    var expires = "";
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days*24*60*60*1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + (value || "")  + expires + "; path=/; samesite=strict; secure";
}

function setSessionCookie(value){
    document.cookie = "SessionCookie=" + (value || "") + "; path=/; samesite=strict; secure";
}

function checkSessionCookie(){
	// Returns cookie value or null
	return((document.cookie.match(/^(?:.*;)?\s*SessionCookie\s*=\s*([^;]+)(?:.*)?$/)||[,null])[1]) // Returns
}

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

//let CookieConsent = getCookie("CookieConsent").replace('{','').replace('}','').split("%2C").find(function(o){return o.match("preferences")}).split(":")[1] == "true";
if(getCookie("CookieConsent") && getCookie("CookieConsent").replace('{','').replace('}','').split("%2C").find(function(o){return o.match("preferences")}).split(":")[1] == "true"){
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
    let sID = checkSessionCookie();
    if (uID == null) {
       // If no user cookie is set, both user cookie and session id is set.
        setCookie("user-id", userID(), daysToExpire);
		if(sID == null){
			var sessionID = userID() + "-s";
			setSessionCookie(sessionID);
		} else{
			var sessionID = sID;
		}
        // Pushing user-id (deviceID) and session-id (sessionID) to database 
		var deviceID = getCookie('user-id');
		var screenWidth = screen.width;
		var screenHeight = screen.height;
		var deviceOS = getOS();
		var deviceVendor = getBrowser();
		if(deviceID != "" && screenWidth != "" && screenHeight != "" && sessionID != ""){
			let xhttp = new XMLHttpRequest();
			xhttp.open("POST", fullUrl + "php/device.php", true);
			xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
			let data = `deviceID=${deviceID}&screenWidth=${screenWidth}&screenHeight=${screenHeight}&deviceOS=${deviceOS}&deviceVendor=${deviceVendor}`;
			data = data.replace( /%20/g, '+' );
			//console.log(data);
		
			// Define what happens on successful data submission
			xhttp.addEventListener( 'load', function(event) {
				if(!xhttp.responseText.includes("Error") && !xhttp.responseText.includes("<br/>")){
					// Succes
					console.log('checkCookieUserID succes');
					//console.error(xhttp.responseText);
					//console.log(deviceID, screenHeight, screenWidth, deviceOS);
				} else{
					// Error
					console.log('checkCookieUserID error');
					console.error(xhttp.responseText);
				}
			});

			// Define what happens in case of error
			xhttp.addEventListener( 'error', function(event) {
				console.log('checkCookieUserID server error');
				console.error(xhttp.responseText);
			});

			xhttp.send(data);
			
			let xhttp2 = new XMLHttpRequest();
			xhttp2.open("POST", fullUrl + "php/session.php", true);
			xhttp2.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
			let data2 = `deviceID=${deviceID}&sessionID=${sessionID}`;
			data2 = data2.replace( /%20/g, '+' );
			//console.log(data2);
			
			xhttp2.addEventListener( 'load', function(event) {
				if(!xhttp2.responseText.includes("Error") && !xhttp.responseText.includes("<br/>")){
					// Succes
					console.log('checkCookieUserID second succes');
					//console.log(deviceID, sessionID);
				} else{
					// Error
					console.log('checkCookieUserID second error');
					console.error(xhttp2.responseText);
				}
			});
			
			// Define what happens in case of error
			xhttp2.addEventListener( 'error', function(event) {
				console.log('checkCookieUserID second server error');
				console.error(xhttp2.responseText);
			});
			
			xhttp2.send(data2);
		}
		return(1);
    } else if (sID == null){
        // Setting session-id (sessionID) if not set, and pushing session-id (sessionID) with user-id (deviceID) to database
        //$(document).ready(function(){
		var deviceID = getCookie('user-id');
		var sessionID = userID() + "-s";
		setSessionCookie(sessionID);
		if(deviceID != "" && sessionID != ""){
			let xhttp = new XMLHttpRequest();
			xhttp.open("POST", fullUrl + "php/session.php", true);
			xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
			let data = `deviceID=${deviceID}&sessionID=${sessionID}`;
			data = data.replace( /%20/g, '+' );
			//console.log(data);

			xhttp.addEventListener( 'load', function(event) {
				if(!xhttp.responseText.includes("Error") && !xhttp.responseText.includes("<br/>")){
					// Succes
					console.log('checkCookieUserID else succes');
					//console.log(deviceID, sessionID);
				} else{
					// Error
					console.log('checkCookieUserID else error');
					console.error(xhttp.responseText);
				}
			});
			
			// Define what happens in case of error
			xhttp.addEventListener( 'error', function(event) {
				console.log('checkCookieUserID else server error');
				console.error(xhttp2.responseText);
			});
			
			xhttp.send(data);
		}
		return(2);
    } else{
		var deviceID = getCookie('user-id');
		//console.log("Cookie update!")
		setCookie("user-id", deviceID, daysToExpire);
		return(3);
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
function saveSession(elapsed, articleID, scrollY, lat, lon){
	if(elapsed != "" && articleID != ""){
		const sessionID = checkSessionCookie();
		let xhttp = new XMLHttpRequest();
		
		// Define what happens on successful data submission
		xhttp.addEventListener( 'load', function(event) {
			if(!xhttp.responseText.includes("Error") && !xhttp.responseText.includes("<br/>")){
				// Succes
				console.log('saveSession succes');
			} else{
				// Error
				console.log('saveSession error');
				console.log(sessionID, elapsed, articleID, scrollY, lat, lon);
				console.error(xhttp.responseText);
				// Attempting to add entry potential missing entry to session
				let deviceID = getCookie('user-id');
				let xhttpSession = new XMLHttpRequest();
				xhttpSession.open("POST", fullUrl + "php/session.php", true);
				xhttpSession.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
				let data = `deviceID=${deviceID}&sessionID=${sessionID}`;
				data = data.replace( /%20/g, '+' );
				//console.log(data);

				xhttpSession.addEventListener( 'load', function(event) {
					if(!xhttpSession.responseText.includes("Error") && !xhttpSession.responseText.includes("<br/>")){
						// Succes
						console.log('Missing session entry added succesfully');
						//console.log(deviceID, sessionID);
						let xhttp = new XMLHttpRequest();
						
						// Define what happens on successful data submission
						xhttp.addEventListener( 'load', function(event) {
							if(!xhttp.responseText.includes("Error") && !xhttp.responseText.includes("<br/>")){
								// Succes
								console.log('saveSession second attempt succes');
							} else{
								// Error
								console.log('saveSession second attempt error');
								console.log(sessionID, elapsed, articleID, scrollY, lat, lon);
								console.error(xhttp.responseText);
							}
						});

						// Define what happens in case of error
						xhttp.addEventListener( 'error', function(event) {
							console.log('saveSession second attempt server error');
							console.error(xhttp.responseText);
						});
						
						xhttp.open("POST", fullUrl + "php/sessionInfo.php", true);
						xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
						let data = `sessionID=${sessionID}&elapsed=${elapsed}&articleID=${articleID}&scrollY=${scrollY}&lat=${lat}&lon=${lon}`;
						data = data.replace( /%20/g, '+' );
						//console.log(data);
						xhttp.send(data);
					} else{
						// Error
						console.log('saveSession else error');
						console.error(xhttpSession.responseText);
					}
				});
				
				// Define what happens in case of error
				xhttpSession.addEventListener( 'error', function(event) {
					console.log('checkCookieUserID else server error');
					console.error(xhttp2.responseText);
				});
				
				xhttpSession.send(data);
			}
		});

		// Define what happens in case of error
		xhttp.addEventListener( 'error', function(event) {
			console.log('saveSession server error');
			console.error(xhttp.responseText);
		});
		
		xhttp.open("POST", fullUrl + "php/sessionInfo.php", true);
		xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
		let data = `sessionID=${sessionID}&elapsed=${elapsed}&articleID=${articleID}&scrollY=${scrollY}&lat=${lat}&lon=${lon}`;
		data = data.replace( /%20/g, '+' );
		//console.log(data);
		xhttp.send(data);
	}
}

/* Function for updating session info at event */
function updateSession(scrollY){
    const sessionID = checkSessionCookie();
    const articleID = document.head.querySelector("[property='bazo:id'][content]").content;
    const endDate = new Date();
    const spentTime = endDate.getTime() - startDate.getTime();
    const elapsed = Math.floor(spentTime/1000);

	if(sessionID !== null && elapsed != "" && articleID != ""){
		let xhttp = new XMLHttpRequest();
		xhttp.open("POST", fullUrl + "php/sessionInfo_update.php", true);
		xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
		let data = `sessionID=${sessionID}&elapsed=${elapsed}&articleID=${articleID}&scrollY=${scrollY}`;
		data = data.replace( /%20/g, '+' );
		//console.log(data);
		
		// Define what happens on successful data submission
		xhttp.addEventListener( 'load', function(event) {
			if(!xhttp.responseText.includes("Error") && !xhttp.responseText.includes("<br/>")){
				// Succes
				console.log('updateSession succes');
			} else{
				// Error
				console.log('updateSession error');
				console.error(xhttp.responseText);
			}
		});

		// Define what happens in case of error
		xhttp.addEventListener( 'error', function(event) {
			console.log('updateSession server error');
			console.error(xhttp.responseText);
		});

		xhttp.send(data);
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

	/* Initiating variables to be updated */
	startDate = new Date();
	let maxScroll = 0; 
	
	const elapsed = 1; // can't be zero, so initial value is 1
	const articleID = document.head.querySelector("[property='bazo:id'][content]").content;
	let scrollY = maxScroll;

	(async function() {
		pos = await getLocation();
		dis = await checkCookieUserID(daysToExpire);
	})().then(() => {
		// If succes
		let lat = pos.coords.latitude.toFixed(3); // Get latitude and generalise position
		let lon = pos.coords.longitude.toFixed(3); // Get longitude and generalise position
		//console.log(pos);
		//console.log(dis);
		saveSession(elapsed, articleID, scrollY, lat, lon);
	}).catch((err) => {
		// If failed
		//console.log(err);
		let lat = "0,0";
		let lon = "0,0";
		saveSession(elapsed, articleID, scrollY, lat, lon);
	});

	/* Updating maxScroll whenever scrolling is happening,
	and updating elapsed and scrollY in database */
	var isScrolling;
	window.addEventListener('scroll', function(event ) {
		// Clear our timeout throughout the scroll
		window.clearTimeout( isScrolling );
		// Set a timeout to run after scrolling ends
		isScrolling = setTimeout(function() {
			if(scrollPercentage() > maxScroll){
				maxScroll = Math.round(scrollPercentage());
			}
			scrollY = maxScroll;
			updateSession(scrollY);
		}, 66);
	}, false);

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
});
}
