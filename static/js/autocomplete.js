/* autocomplete.js for base.html

Maurice Kingma
Minor Programmeren - Web App Studio

Javascript for getting autocomplete results
*/

// wait for page to load
document.addEventListener('DOMContentLoaded', () => {

    if (document.getElementById('autolist')) {
        autolist = document.getElementById('autolist');
    } else {
        autolist = document.querySelector('.autolist');
    };

    autolist.style.display = 'none';
    autolist.innerHTML = ''


    document.querySelector('.navbar-toggler').onclick = () => {
        autolist.style.display = 'none';
    }

    // select regular search input field
    document.querySelector('#autocomplete').oninput = () => {
        const query = document.querySelector('#autocomplete').value;

        if (query.length <= 2) {
            autolist.innerHTML = '';
            autolist.style.display = 'none';
        } else {
            const request = new XMLHttpRequest();
            request.open('POST', window.location.origin + '/autocomplete', false);

            request.onload = () => {
                autolist.innerHTML = '';
                autolist.style.display = '';
                const autoList = JSON.parse(request.responseText);
                if ("recommList" in autoList) {
                    var recomTitle = document.createElement('DIV');
                    recomTitle.className = "btn btn-danger btn-sm"
                    recomTitle.innerHTML = "AANRADERS"
                    recomTitle.id = "checklabel"
                    autolist.appendChild(recomTitle);
                    for (key in autoList["recommList"]) {
                        var item = document.createElement('DIV');
                        var a = document.createElement('A');
                        a.href = window.location.origin + "/locatie/" + encodeURI(key)+ '/' + encodeURI(autoList["recommList"][key])
                        item.className = "item"
                        var text = document.createTextNode(key);
                        item.appendChild(text);
                        a.appendChild(item);
                        autolist.appendChild(a);
                        };
                };
                if ("categList" in autoList) {
                    for (key in autoList["categList"]) {
                        var categTitle = document.createElement('DIV');
                        categTitle.className = "autoTitle"
                        categIcon = document.createElement('I');
                        console.log(key);
                        categIcon.className = "fas fa-" + autoList["ICON_DICT"][key]
                        categTitle.appendChild(categIcon)
                        var text = document.createTextNode(autoList["TYPES_DICT"][key]);
                        categTitle.appendChild(text);
                        autolist.appendChild(categTitle);
                        for (key1 in autoList["categList"][key]) {
                            var item = document.createElement('DIV');
                            var a = document.createElement('A');
                            a.href = window.location.origin + "/locatie/" + encodeURI(key1)+ '/' + encodeURI(autoList["categList"][key][key1])
                            item.className = "item"
                            var text = document.createTextNode(key1);
                            a.appendChild(item);
                            item.appendChild(text);
                            autolist.appendChild(a);
                        };
                    };
                };
                if (autolist.innerHTML == '') {
                    autolist.style.display = 'none';
                    autolist.innerHTML = '';
                };
            };

            // add username to request
            const data = new FormData();
            data.append('query', query);

            // send request
            request.send(data);

        };
    };
});
