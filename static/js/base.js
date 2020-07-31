/* base.js for base.html

Maurice Kingma
Minor Programmeren - Web App Studio

Javascript for checking login input
*/

// wait for page to load
document.addEventListener('DOMContentLoaded', () => {

	if (document.querySelector('#login')) {

		// select register button and activate function on click
		document.querySelector('#login').onclick = () => {

			// check if input and get username
			if (document.querySelector('#usernameinput').value.length == 0) {
				event.preventDefault();
				event.stopPropagation();
				document.querySelector('#invalidusername').innerHTML = "Geef een gebruikersnaam op";
			} else {
				document.querySelector('#invalidusername').innerHTML = "";
			}
			if (document.querySelector('#passwordinput').value.length == 0) {
				event.preventDefault();
				event.stopPropagation();
				document.querySelector('#invalidpassword').innerHTML = "Geef een wachtwoord op";
			} else {
				document.querySelector('#invalidpassword').innerHTML = "";

			};
		};
	};
});
