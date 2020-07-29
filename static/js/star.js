/* star.js for search.html and location.html

Maurice Kingma
Minor Programmeren - Web App Studio

Javascript for displaing rating as amount of stars
*/

function stars() {
	const elements = document.querySelectorAll('#stars');
	for (var j = 0; j < elements.length; j++) {
		const rating = Math.round(elements[j].innerHTML * 2) / 2;

	  // Round to nearest half

	    let output = [];

	    // Append all the filled whole stars
	    for (var i = rating; i >= 1; i--)
	      output.push('<i class="fas fa-star" aria-hidden="true"></i>&nbsp;');

	    // If there is a half a star, append it
	    if (i == .5) output.push('<i class="fas fa-star-half" aria-hidden="true"></i>&nbsp;');

	    // Fill the empty stars
	    for (let i = (5 - rating); i >= 1; i--)
	      output.push('<i class="far fa-star" aria-hidden="true"></i>&nbsp;');


		elements[j].innerHTML = output.join('')
		elements[j].id = ""
	};
};

// wait for page to load and start function
document.addEventListener('DOMContentLoaded', stars());
