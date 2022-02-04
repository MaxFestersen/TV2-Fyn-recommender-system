let cookieString = '';
cookieEnd =  ' path=/; max-age=3600'
document.cookie = 'name=device-information;' + cookieEnd;
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
