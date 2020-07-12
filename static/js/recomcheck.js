/* recomcheck.js for createnew.html and changenew.html

Maurice Kingma
Minor Programmeren - Web App Studio

Javascript for checking input when publishing
*/

// wait for page to load
document.addEventListener('DOMContentLoaded', () => {

    // select submitbutton
    document.querySelector('input[name="submit"]').onclick = () => {

        // get checkbox and see if it is checked
        if (document.querySelector('input[name="visible"]').checked) {
            if (document.getElementById('review').length > 0) {
                document.querySelector('#review').setCustomValidity('')
            } else {
                document.querySelector('#review').setCustomValidity('invalid')
                document.body.scrollTop = 0; // For Safari
                document.documentElement.scrollTop = 0; // For Chrome, Firefox, IE and Opera
            }
        } else {
            document.querySelector('#review').setCustomValidity('')
        }
    };
});
