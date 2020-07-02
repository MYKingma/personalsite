/* registration.js for register.html

Maurice Kingma
Minor Programmeren - Web App Studio

Javascript for checking input and availability email and username
*/

// wait for page to load
document.addEventListener('DOMContentLoaded', () => {
    // select register button and activate function on click
    document.querySelector('#emailbutton').onclick = () => {

        // check if input and get email
        if (document.querySelector('#emailinput').value.length > 0) {
            const email = document.querySelector('#emailinput').value;

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
                    document.querySelector('#emailinput').setCustomValidity('invalid');
                } else {
                    document.querySelector('#emailinput').setCustomValidity('');
                    document.querySelector('#emailerrormessage').innerHTML = "Geef een geldig e-mailadres op";
                };
            };

            // add email to request
            const data = new FormData();
            data.append('email', email);

            // send request
            request.send(data);

        };
    };
    
    // select register button and activate function on click
	document.querySelector('#emailbuttonsmall').onclick = () => {

		// check if input and get email
		if (document.querySelector('#emailinputsmall').value.length > 0) {
			const email = document.querySelector('#emailinputsmall').value;

			// create new http request
			const request = new XMLHttpRequest();
			request.open('POST', '/emailcheck');
			request.onload = () => {
				const data = JSON.parse(request.responseText);

				// show message if not available
                if (data.success) {
					const contents = `E-mailadres ${email} al in gebruik`;
                	document.querySelector('#emailerrormessagesmall').innerHTML = contents;

					// set input to invalid for bootstrap validation
					document.querySelector('#emailinputsmall').setCustomValidity('invalid');
                } else {
					document.querySelector('#emailinputsmall').setCustomValidity('');
					document.querySelector('#emailerrormessagesmall').innerHTML = "Geef een geldig e-mailadres op";
                };
			};

			// add email to request
			const data = new FormData();
			data.append('email', email);

			// send request
			request.send(data);

		};
	};
});
