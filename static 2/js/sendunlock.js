/* sendunlock.js for base.html

Maurice Kingma
Minor Programmeren - Web App Studio

Javascript for unlocking send button
*/

// wait for page to load
document.addEventListener('DOMContentLoaded', () => {
	// select checkbox and activate delete button if checked
	document.getElementById('unlock').onclick = () => {
		const buttons = document.querySelectorAll('#locked');
		for (var i = 0; i < buttons.length; i++) {
			if (buttons[i].disabled == true) {
				buttons[i].disabled = false;
				document.getElementById('lock').className = "fas fa-unlock"
			} else {
				buttons[i].disabled = true;
				document.getElementById('lock').className = "fas fa-lock"
			};
		};
	};
});
