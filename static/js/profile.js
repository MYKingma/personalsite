/* registration.js for register.html

Maurice Kingma
Minor Programmeren - Web App Studio

Javascript for checking input and availability email and username
*/

// wait for page to load
document.addEventListener('DOMContentLoaded', () => {

    // select register button and activate function on click
	document.querySelector('#passwordbutton').onclick = () => {

		// check if input and get passwords
		if (document.querySelector('#password1').value.length > 0) {
			if (document.querySelector('#password2').value.length > 0) {
				const password1 = document.querySelector('#password1').value;
				const password2 = document.querySelector('#password2').value;
				if (password1 != password2) {
					document.querySelector('#invalidpassword1').innerHTML = "";
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
	
    // select register button and activate function on click
	document.querySelector('#passwordbuttonsmall').onclick = () => {

		// check if input and get passwords
		if (document.querySelector('#password1small').value.length > 0) {
			if (document.querySelector('#password2small').value.length > 0) {
				const password1 = document.querySelector('#password1small').value;
				const password2 = document.querySelector('#password2small').value;
				if (password1 != password2) {
					document.querySelector('#invalidpassword1small').innerHTML = "";
					document.querySelector('#passworderrormessagesmall').innerHTML = "Wachtwoorden komen niet overeen";
					document.querySelector('#password1small').setCustomValidity('invalid');
					document.querySelector('#password2small').setCustomValidity('invalid');
				} else {
					document.querySelector('#password1small').setCustomValidity('');
					document.querySelector('#password2small').setCustomValidity('');
				};
			} else {
				document.querySelector('#password1small').setCustomValidity('');
				document.querySelector('#invalidpasswordsmall').innerHTML = "Geef een wachtwoord op";
				document.querySelector('#passworderrormessagesmall').innerHTML = "Herhaal het wachtwoord";
			};
		};
	};
});
