/* resetpass.js for resetpass.html

Maurice Kingma
Minor Programmeren - Web App Studio

Javascript for checking input passwords when resetting
*/

// wait for page to load
document.addEventListener('DOMContentLoaded', () => {
	
	// select register button and activate function on click
	document.querySelector('#resetpass').onclick = () => {
		// check if input and get passwords
		if (document.querySelector('#password1').value.length > 0) {
			if (document.querySelector('#password2').value.length > 0) {
				const password1 = document.querySelector('#password1').value;
				const password2 = document.querySelector('#password2').value;
				if (password1 != password2) {
					document.querySelector('#invalidpassword').innerHTML = "";
					document.querySelector('#passworderrormessage').innerHTML = "Wachtwoorden komen niet overeen";
					document.querySelector('#password1').setCustomValidity('invalid');
					document.querySelector('#password2').setCustomValidity('invalid');
				} else {
					document.querySelector('#password1').setCustomValidity('');
					document.querySelector('#password2').setCustomValidity('');
				};
			} else {
				document.querySelector('#password1').setCustomValidity('');
				document.querySelector('#invalidpassword').innerHTML = "Geef een wachtwoord op";
				document.querySelector('#passworderrormessage').innerHTML = "Herhaal het wachtwoord";
			};
		};
	};
});