/* function for setting cookies*/
function sdu_1_setCookie(name,value,days) {
    let expires = "";
    if (days) {
        var  date = new Date();
        date.setTime(date.getTime() + (days*24*60*60*1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + (value || "")  + expires + "; path=/; samesite=strict; secure";
}

function sdu_1_setSessionCookie(value){
    document.cookie = "sdu_1_SessionCookie=" + (value || "") + "; path=/; samesite=strict; secure";
}

function sdu_1_checkSessionCookie(){
	// Returns cookie value or null
	return((document.cookie.match(/^(?:.*;)?\s*sdu_1_SessionCookie\s*=\s*([^;]+)(?:.*)?$/)||[,null])[1]) // Returns
}

/* function for getting cookie value, returns null if none set for a name*/ 
function sdu_1_getCookie(name) {
	let nameEQ = name + "=";
	let ca = document.cookie.split(';');
	for(var i=0;i < ca.length;i++) {
		let c = ca[i];
		while (c.charAt(0)==' ') c = c.substring(1,c.length);
		if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
	}
	return null;
}

//let CookieConsent = sdu_1_getCookie("CookieConsent").replace('{','').replace('}','').split("%2C").find(function(o){return o.match("preferences")}).split(":")[1] == "true";
if(sdu_1_getCookie("CookieConsent") && sdu_1_getCookie("CookieConsent").replace('{','').replace('}','').split("%2C").find(function(o){return o.match("preferences")}).split(":")[1] == "true"){
/* sdu_1_userID is a string that consists of number of miliseconds since 1/1-1970 and a random 3 character integer */
function sdu_1_userID() {
    let date = Date.now()
    let random = Math.floor(Math.random() * 1000)
    return date + "-" + random
}

function sdu_1_getOS() {
    let OSName = "Unknown OS";
    if (navigator.userAgent.indexOf("Win") != -1) OSName = "Windows";
    if (navigator.userAgent.indexOf("Mac") != -1) OSName = "Macintosh";
    if (navigator.userAgent.indexOf("Linux") != -1) OSName = "Linux";
    if (navigator.userAgent.indexOf("Android") != -1) OSName = "Android";
    if (navigator.userAgent.indexOf("like Mac") != -1) OSName = "iOS";
    return OSName;
}

function sdu_1_getBrowser() {
	// inspired by https://codepedia.info/detect-browser-in-javascript
	let browserName = (function (agent) {
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
function sdu_1_checkCookieuserID(daysToExpire) {
    let uID = sdu_1_getCookie('sdu_1_user-id');
    let sID = sdu_1_checkSessionCookie();
    if (uID == null) {
       // If no user cookie is set, both user cookie and session id is set.
        sdu_1_setCookie("sdu_1_user-id", sdu_1_userID(), daysToExpire);
		if(sID == null){
			var sessionID = sdu_1_userID() + "-s";
			sdu_1_setSessionCookie(sessionID);
		} else{
			var sessionID = sID;
		}
        // Pushing user-id (deviceID) and session-id (sessionID) to database 
		let deviceID = sdu_1_getCookie('sdu_1_user-id');
		let screenWidth = screen.width;
		let screenHeight = screen.height;
		let deviceOS = sdu_1_getOS();
		let deviceVendor = sdu_1_getBrowser();
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
					console.log('sdu_1_checkCookieuserID succes');
					//console.error(xhttp.responseText);
					//console.log(deviceID, screenHeight, screenWidth, deviceOS);
				} else{
					// Error
					console.log('sdu_1_checkCookieuserID error');
					console.error(xhttp.responseText);
				}
			});

			// Define what happens in case of error
			xhttp.addEventListener( 'error', function(event) {
				console.log('sdu_1_checkCookieuserID server error');
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
					console.log('sdu_1_checkCookieuserID second succes');
					//console.log(deviceID, sessionID);
				} else{
					// Error
					console.log('sdu_1_checkCookieuserID second error');
					console.error(xhttp2.responseText);
				}
			});
			
			// Define what happens in case of error
			xhttp2.addEventListener( 'error', function(event) {
				console.log('sdu_1_checkCookieuserID second server error');
				console.error(xhttp2.responseText);
			});
			
			xhttp2.send(data2);
		}
		return(1);
    } else if (sID == null){
        // Setting session-id (sessionID) if not set, and pushing session-id (sessionID) with user-id (deviceID) to database
        //$(document).ready(function(){
		let deviceID = sdu_1_getCookie('sdu_1_user-id');
		let sessionID = sdu_1_userID() + "-s";
		sdu_1_setSessionCookie(sessionID);
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
					console.log('sdu_1_checkCookieuserID else succes');
					//console.log(deviceID, sessionID);
				} else{
					// Error
					console.log('sdu_1_checkCookieuserID else error');
					console.error(xhttp.responseText);
				}
			});
			
			// Define what happens in case of error
			xhttp.addEventListener( 'error', function(event) {
				console.log('sdu_1_checkCookieuserID else server error');
				console.error(xhttp2.responseText);
			});
			
			xhttp.send(data);
		}
		return(2);
    } else{
		var deviceID = sdu_1_getCookie('sdu_1_user-id');
		//console.log("Cookie update!")
		sdu_1_setCookie("sdu_1_user-id", deviceID, daysToExpire);
		return(3);
	}
}

/* Get user location */
/* Inspiration
	- https://www.w3schools.com/html/html5_geolocation.asp
	- https://tutorialmeta.com/question/javascript-pass-geolocation-as-string-variable
*/
/*function getLocation() {
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
}*/

/* Function for saving session info at first page load */
function sdu_1_saveSession(elapsed, articleID, scrollY){
	if(elapsed != "" && articleID != ""){
		const sessionID = sdu_1_checkSessionCookie();
		let xhttp = new XMLHttpRequest();
		
		// Define what happens on successful data submission
		xhttp.addEventListener( 'load', function(event) {
			if(!xhttp.responseText.includes("Error") && !xhttp.responseText.includes("<br/>")){
				// Succes
				console.log('sdu_1_saveSession succes');
			} else{
				// Error
				console.log('sdu_1_saveSession error');
				console.log(sessionID, elapsed, articleID, scrollY);
				console.error(xhttp.responseText);
				// Attempting to add entry potential missing entry to session
				let deviceID = sdu_1_getCookie('sdu_1_user-id');
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
								console.log('sdu_1_saveSession second attempt succes');
							} else{
								// Error
								console.log('sdu_1_saveSession second attempt error');
								console.log(sessionID, elapsed, articleID, scrollY);
								console.error(xhttp.responseText);
							}
						});

						// Define what happens in case of error
						xhttp.addEventListener( 'error', function(event) {
							console.log('sdu_1_saveSession second attempt server error');
							console.error(xhttp.responseText);
						});
						
						xhttp.open("POST", fullUrl + "php/sessionInfo.php", true);
						xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
						let data = `sessionID=${sessionID}&elapsed=${elapsed}&articleID=${articleID}&scrollY=${scrollY}`;
						data = data.replace( /%20/g, '+' );
						//console.log(data);
						xhttp.send(data);
					} else{
						// Error
						console.log('sdu_1_saveSession else error');
						console.error(xhttpSession.responseText);
					}
				});
				
				// Define what happens in case of error
				xhttpSession.addEventListener( 'error', function(event) {
					console.log('sdu_1_saveSession else server error');
					console.error(xhttp2.responseText);
				});
				
				xhttpSession.send(data);
			}
		});

		// Define what happens in case of error
		xhttp.addEventListener( 'error', function(event) {
			console.log('sdu_1_saveSession server error');
			console.error(xhttp.responseText);
		});
		
		xhttp.open("POST", fullUrl + "php/sessionInfo.php", true);
		xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
		let data = `sessionID=${sessionID}&elapsed=${elapsed}&articleID=${articleID}&scrollY=${scrollY}`;
		data = data.replace( /%20/g, '+' );
		//console.log(data);
		xhttp.send(data);
	}
}

/* Function for updating session info at event */
function sdu_1_updateSession(scrollY){
    const sessionID = sdu_1_checkSessionCookie();
    const articleID = document.head.querySelector("[property='bazo:id'][content]").content;
    const endDate = new Date();
    const spentTime = endDate.getTime() - sdu_1_startDate.getTime();
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
				console.log('sdu_1_updateSession succes');
			} else{
				// Error
				console.log('sdu_1_updateSession error');
				console.error(xhttp.responseText);
			}
		});

		// Define what happens in case of error
		xhttp.addEventListener( 'error', function(event) {
			console.log('sdu_1_updateSession server error');
			console.error(xhttp.responseText);
		});

		xhttp.send(data);
	}
    sdu_1_startDate = new Date(); // resetting start date after each update
}

/* Function for computing percentage of page scrolled */
function sdu_1_scrollPercentage() {
    let scrollPercentage = (((document.documentElement.scrollTop + document.body.scrollTop) / (document.documentElement.scrollHeight - document.documentElement.clientHeight) || 0) * 100);
    return scrollPercentage;
}

// path of cookie scripts
//let script = document.currentScript;
//let fullUrl = script.src.split('/').slice(0, -2).join('/')+'/';
let fullUrl = "https://recommendations.tv2fyn.dk:8443/";

/* Pushing session info to database when page loads */
window.addEventListener('load', (event) => {
	let daysToExpire = 30; // number of days before cookie expires

	/* Initiating variables to be updated */
	sdu_1_startDate = new Date();
	let maxScroll = 0; 
	
	const elapsed = 1; // can't be zero, so initial value is 1
	const articleID = document.head.querySelector("[property='bazo:id'][content]").content;
	let scrollY = maxScroll;
	
	sdu_1_checkCookieuserID(daysToExpire);
	sdu_1_saveSession(elapsed, articleID, scrollY);

	/* Updating maxScroll whenever scrolling is happening,
	and updating elapsed and scrollY in database */
	let isScrolling;
	window.addEventListener('scroll', function(event ) {
		// Clear our timeout throughout the scroll
		window.clearTimeout( isScrolling );
		// Set a timeout to run after scrolling ends
		isScrolling = setTimeout(function() {
			if(sdu_1_scrollPercentage() > maxScroll){
				maxScroll = Math.round(sdu_1_scrollPercentage());
			}
			let scrollY = maxScroll;
			sdu_1_updateSession(scrollY);
		}, 66);
	}, false);

	/* Pushing updated elapsed time and scrollY to database, when switching tabs */
	document.addEventListener('visibilitychange', function(){
		if (document.visibilityState === 'hidden') {
			let scrollY = maxScroll;
			sdu_1_updateSession(scrollY);
		}
	});

	/*document.addEventListener('click', function(){
		let scrollY = maxScroll;
		sdu_1_updateSession(scrollY);
	});*/
});
}
