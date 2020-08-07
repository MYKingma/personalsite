/* hide.js for search.html

Maurice Kingma
Minor Programmeren - Web App Studio

Javascript for hiding locations from website
*/

// wait for page to load
document.addEventListener('DOMContentLoaded', () => {
	document.querySelectorAll('.hideButton').forEach (hideButton => {
		hideButton.onclick = () => {
			var place_id = hideButton.dataset.place_id;
			var name = hideButton.dataset.name;
			event.stopPropagation();
			event.preventDefault();

			if (confirm('Weet je zeker dat je deze locatie van de website wil verwijderen?')) {

				const request = new XMLHttpRequest();
				request.open('POST', window.location.origin + '/hidelocation', false);

				request.onload = () => {
					const data = JSON.parse(request.responseText);

					if (data.success) {
						var location = document.querySelector('[data-hide="' + place_id + '"]');
						location.remove()
					};
				};

				// add username to request
				const data = new FormData();
				data.append('place_id', place_id);
				data.append('name', name);

				// send request
				request.send(data);
			};
		};
	});
});
