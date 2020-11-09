/* hidealert.js

Maurice Kingma

Javascript for hiding alerts
*/

// wait for page to load
document.addEventListener('DOMContentLoaded', () => {
	var alert = document.querySelector('#alert')
    setTimeout(function(){
        //do what you need here
        alert.classList.add('slideaway')
        setTimeout(function(){
            alert.style.display = "none"

        }, 200);
    }, 2000);

});
