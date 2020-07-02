/* filter.js for base.html

Maurice Kingma
Minor Programmeren - Web App Studio

Javascript for setting select menu with filters
*/

// wait for page to load
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('recommendinput').oninput = () => {
        const hideoptions = document.querySelectorAll('[data-ser]');
        if (document.getElementById('recommendinput').checked) {
            for (var i = 0; i < hideoptions.length; i++) {
                var div = document.createElement('div');
                div.innerHTML = hideoptions[i].innerHTML;
                div.dataset.ser = "True";
                div.className = 'hidden';
                div.value = hideoptions[i].value;
                hideoptions[i].parentElement.replaceChild(div, hideoptions[i]);
            }
        } else {
            for (var i = 0; i < hideoptions.length; i++) {
                var option = document.createElement('option');
                option.innerHTML = hideoptions[i].innerHTML;
                option.dataset.ser = "True";
                option.className = '';
                option.value = hideoptions[i].value;
                hideoptions[i].parentElement.replaceChild(option, hideoptions[i]);
            }
        }
        const showoptions = document.querySelectorAll('[data-rec]');
        if (document.getElementById('recommendinput').checked) {
            for (var i = 0; i < showoptions.length; i++) {
                var option = document.createElement('option');
                option.innerHTML = showoptions[i].dataset.value;
                option.dataset.rec = "True";
                option.value = showoptions[i].value;
                var select = document.querySelector('#typeinput');
                select.appendChild(option);
                showoptions[i].remove();
            }
        } else {
            for (var i = 0; i < showoptions.length; i++) {
                var div = document.createElement('div');
                div.dataset.value = showoptions[i].innerHTML;
                div.dataset.rec = "True";
                div.className = 'hidden';
                div.value = showoptions[i].value;
                showoptions[i].parentElement.replaceChild(div, showoptions[i]);
            }
        }
    };
});
