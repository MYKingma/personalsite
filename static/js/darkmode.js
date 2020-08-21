/* darkmode.js for implementing dark mode

Maurice Kingma
Minor Programmeren - Web App Studio

*/
function setTheme() {
    if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
        document.querySelector('#html').className = "dark";
    }
    window.matchMedia('(prefers-color-scheme: dark)').addListener(function (e) {
        if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
            document.querySelector('#html').className = "dark";
        } else {
            document.querySelector('#html').className = "";
        }
    });
}

// wait for page to load
document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('[property="preferredtheme"]').content == "light") {
        document.querySelector('#html').className == ""
    } else if (document.querySelector('[property="preferredtheme"]').content == "dark") {
        document.querySelector('#html').className = "dark";
    } else {
            setTheme()
        };
    });
