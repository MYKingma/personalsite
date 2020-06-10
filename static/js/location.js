/* location.js for location.html

Maurice Kingma
Minor Programmeren - Web App Studio

Javascript for functions on location page
*/

// wait for page to load
document.addEventListener('DOMContentLoaded', () => {
	document.querySelectorAll('#jsbutton').forEach(button => {
		button.onclick = () => {
			const place = button.dataset.location;
			const action = button.dataset.button;
			const locationname = button.dataset.locationname
		
			// create new http request
			const request = new XMLHttpRequest();
			request.open('POST', '/location/action');
			request.onload = () => {						
				const data = JSON.parse(request.responseText);
			
				// show message if not available					
	            if (data.success && action == "favourite") {
					if (document.querySelector('#heart').className == "fas fa-heart") {
						document.querySelector('#heart').className = "far fa-heart";
					} else {
						document.querySelector('#heart').className = "fas fa-heart";
					};
	            } else if (data.success && action == "recommend") {
	            	document.querySelector('#finger').className = "fas fa-hand-point-up";
					const message = document.createElement('DIV');
					message.setAttribute("class", "alert alert-success alert-dismissible");
					const child = document.createElement('A');
					child.setAttribute("href", "#");
					child.setAttribute("class", "close");
					child.setAttribute("data-dismiss", "alert");
					child.setAttribute("arai-label", "close");
					child.innerHTML = "&times;"
					const text = "Aanvraag voor meer informatie verstuurd, houd je inbox in de gaten!"
					message.appendChild(child);
					message.innerHTML = message.innerHTML + text;
					document.querySelector('.message-container').appendChild(message);
					window.scrollTo(0, 0)
	            } else if (!data.success && action == "recommend") {
					const message = document.createElement('DIV');
					message.setAttribute("class", "alert alert-warning alert-dismissible");
					const child = document.createElement('A');
					child.setAttribute("href", "#");
					child.setAttribute("class", "close");
					child.setAttribute("data-dismiss", "alert");
					child.setAttribute("arai-label", "close");
					child.innerHTML = "&times;"
					const text = "Aanvraag al verstuurd, check je spam inbox als je al langer wacht"
					message.appendChild(child);
					message.innerHTML = message.innerHTML + text;
					document.querySelector('.message-container').appendChild(message);
					window.scrollTo(0, 0)
	            }
			};
		
			// add username to request
			const data = new FormData();
			data.append('place_id', place);
			data.append('button', action);
			data.append('locationname', locationname);
		
			// send request
			request.send(data);
		};
	});
	document.querySelectorAll('#upvote').forEach(button => {
		button.onclick = () => {
			const action = "upvote";
			const review = button.dataset.review_id;
		
			// create new http request
			const request = new XMLHttpRequest();
			request.open('POST', '/location/action');
			
			request.onload = () => {
				const data = JSON.parse(request.responseText);
				if (data.success) {
					if (data.status == "added") {
						button.className = "btn btn-danger btn-sm"
						button.innerHTML = `Nuttig (${data.count})`
					}
					if (data.status == "deleted") {
						button.className = "btn btn-outline-danger btn-sm"
						button.innerHTML = `Nuttig (${data.count})`
					}
				};
			};
			// add review_id to request
			const data = new FormData();
			data.append('review_id', review);
			data.append('button', action);
					
			// send request
			request.send(data);
			
		};
	});
	
	document.querySelector('#review').onclick = () => {
		radios = document.querySelectorAll('[data-input]');
		for (i = 0; i < radios.length; i++) {
			if (radios[i].checked) {
				var input = true
				break
			} else {
				var input = false
			};
		};
		if (!input) {
			event.preventDefault();
			event.stopPropagation();
			document.querySelector('.errorrev').innerHTML = "Geef minimaal een ster-beoordeling"
		};
	};
});