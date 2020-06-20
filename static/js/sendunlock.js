/* sendunlock.js for base.html

Maurice Kingma
Minor Programmeren - Web App Studio

Javascript for unlocking send button
*/

// wait for page to load
document.addEventListener('DOMContentLoaded', () => {
	// select checkbox and activate delete button if checked
	document.getElementById('unlock').oninput = () => {
		const buttons = document.querySelectorAll('#locked');
		for (var i = 0; i < buttons.length; i++) {
			if (document.getElementById('unlock').checked) {
				buttons[i].disabled = false;
			} else {
				buttons[i].disabled = true;
			};
		};
	};
});
