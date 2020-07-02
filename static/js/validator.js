/* validator.js for base.html

Maurice Kingma
Minor Programmeren - Web App Studio

Javascript for checking login input (bootstrap validator)
*/

// bootstrap validation javascript
// Example starter JavaScript for disabling form submissions if there are invalid fields
(function() {
  'use strict';
  document.addEventListener('DOMContentLoaded', function() {
    // Fetch all the forms we want to apply custom Bootstrap validation styles to
    var forms = document.getElementsByClassName('needs-validation');
    // Loop over them and prevent submission
    var validation = Array.prototype.filter.call(forms, function(form) {
      form.addEventListener('submit', function(event) {
        if (form.checkValidity() === false) {
          event.stopPropagation();
		  event.preventDefault();
	  } else {

	  }
        form.classList.add('was-validated');
      }, false);
    });
  }, false);
})();
