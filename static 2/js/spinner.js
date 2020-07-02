/* spinner.js for search.html

Maurice Kingma
Minor Programmeren - Web App Studio

Javascript for displaing spinner when loading
*/

// wait for page to load
document.addEventListener('DOMContentLoaded', () => {
	document.getElementById('spinnerbutton').onclick = () => {
		var spinner = document.getElementById('showspinner');
		spinner.style.display = "";
	};
})
