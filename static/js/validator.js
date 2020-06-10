/* validator.js for base.html

Maurice Kingma
Minor Programmeren - Web App Studio

Javascript for checking login input (bootstrap validator)
*/

// bootstrap validation javascript
document.addEventListener('DOMContentLoaded', () => {
	var forms = document.getElementsByClassName('needs-validation');
	var validation = Array.prototype.filter.call(forms, function(form) {
		form.addEventListener('submit', function(event) {
			if (form.checkValidity() === false) {
				event.preventDefault();
				event.stopPropagation();
			};
			form.classList.add('was-validated');
		}, false);
    });
}, false);