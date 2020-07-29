/* loadhighlight.js for guide.html

Maurice Kingma
Minor Programmeren - Web App Studio

Javascript for loading previous highlighted locations
*/

// wait for page to load
document.addEventListener('DOMContentLoaded', () => {

    var week = document.querySelector('[data-week]').dataset.week;
    document.querySelector('[data-shift="1"]').style.display = "none"

    document.querySelectorAll('#previousHighlight').forEach(item => {
        item.onclick = () => {
            var shift = item.dataset.shift;

            const request = new XMLHttpRequest();
			request.open('POST', window.location.origin + '/loadhighlight', false);

            request.onload = () => {
                const data = JSON.parse(request.responseText);
                if (data.previous) {
                    document.querySelector('[data-shift="-1"]').style.display = ""
                } else {
                    document.querySelector('[data-shift="-1"]').style.display = "none"
                }
                if (data.next) {
                    document.querySelector('[data-shift="1"]').style.display = ""
                } else {
                    document.querySelector('[data-shift="1"]').style.display = "none"
                }
                document.querySelector('.highlighttitle').innerHTML = data.name
                document.querySelector('.description').innerHTML = data.description
                if (data.totalshift == 0) {
                    document.querySelector('#shift').innerHTML = ""
                    document.querySelector('#shifttext').innerHTML = "deze week"
                } else if (data.totalshift == 1) {
                    document.querySelector('#shift').innerHTML = data.totalshift;
                    document.querySelector('#shifttext').innerHTML = "week geleden";
                } else {
                    document.querySelector('#shift').innerHTML = data.totalshift;
                    document.querySelector('#shifttext').innerHTML = "weken geleden";
                }
                week = data.week
                document.querySelector('#previousPriceLevel').innerHTML = data.linkinfo.price_level + " -";
                document.querySelector('#previousTypes').innerHTML = "";
                document.querySelector('#previousRecLabel').innerHTML = "";
                for (var i = 0; i < data.types.length; i++) {
                    var icon = document.createElement('I');
                    icon.className = "fas fa-" + data.types[i];
                    document.querySelector('#previousTypes').appendChild(icon);
                    var text = document.createTextNode(' ');
                    document.querySelector('#previousTypes').appendChild(text);
                };
                if (data.linkinfo.recommended) {
                    var p = document.createElement('P');
                    var button = document.createElement('BUTTON');
                    button.className = "btn btn-danger btn-sm";
                    button.innerHTML = "AANRADER";
                    var i = document.createElement('I');
                    i.className = "fas fa-medal";
                    button.appendChild(i);
                    p.appendChild(button);
                    document.querySelector('#previousRecLabel').appendChild(p);
                }

                document.querySelector('#previousImg').style.backgroundImage = "url('" + data.linkinfo.photos + "')";
                document.querySelector('#previousLink').href = window.location.origin + "/stadsgids/locatie/" + data.linkinfo.name + "/" + data.linkinfo.place_id
                document.querySelector('#previousName').innerHTML = data.linkinfo.name;
                var span = document.createElement('SPAN');
                span.id = "stars";
                span.innerHTML = data.linkinfo.rating;
                document.querySelector('#previousStars').innerHTML = ""
                document.querySelector('#previousStars').appendChild(span)
                document.querySelector('#previousAddress').innerHTML = data.linkinfo.formatted_address[0];
                stars()
                zenscroll.to(document.querySelector('#top'))
            };

            // add username to request
			const data = new FormData();
			data.append('week', week);
            data.append('shift', shift);

			// send request
			request.send(data);
        };
    });
});