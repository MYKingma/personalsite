/* registration.js for register.html

Maurice Kingma
Minor Programmeren - Web App Studio

Javascript for checking input and availability email and username
*/

// wait for page to load
document.addEventListener('DOMContentLoaded', () => {

	// select register button and activate function on click
	document.querySelector('#button').onclick = () => {

		// check if input and get username
		if (document.querySelector('#username').value.length > 0) {
			const username = document.querySelector('#username').value;

			// create new http request
			const request = new XMLHttpRequest();
			request.open('POST', '/usernamecheck');

			request.onload = () => {
				const data = JSON.parse(request.responseText);

				// show message if not available
                if (data.success) {
					const contents = `Gebruikersnaam ${username} al in gebruik`;
                	document.querySelector('#usernameerrormessage').innerHTML = contents;

					// set input to invalid for bootstrap validation
					document.querySelector('#username').setCustomValidity('invalid');
                } else {
					document.querySelector('#username').setCustomValidity('');
                };
			};

			// add username to request
			const data = new FormData();
			data.append('username', username);

			// send request
			request.send(data);
		};

		// check if input and get email
		if (document.querySelector('#email').value.length > 0) {
			const email = document.querySelector('#email').value;

			// create new http request
			const request = new XMLHttpRequest();
			request.open('POST', '/emailcheck');
			request.onload = () => {
				const data = JSON.parse(request.responseText);

				// show message if not available
                if (data.success) {
					const contents = `E-mailadres ${email} al in gebruik`;
                	document.querySelector('#emailerrormessage').innerHTML = contents;

					// set input to invalid for bootstrap validation
					document.querySelector('#email').setCustomValidity('invalid');
                } else {
					document.querySelector('#email').setCustomValidity('');
					document.querySelector('#emailerrormessage').innerHTML = "Geef een geldig e-mailadres op";
                };
			};

			// add email to request
			const data = new FormData();
			data.append('email', email);

			// send request
			request.send(data);

		};

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
	$(document).ready(function(){
		$('[data-toggle="tooltip"]').tooltip();   
	});
});
