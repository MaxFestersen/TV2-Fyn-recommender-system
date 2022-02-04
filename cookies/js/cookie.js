let cookieString = '';
cookieEnd =  ' path=/; max-age=3600'
document.cookie = 'name=device-information;' + cookieEnd;
console.log(document.cookie);
