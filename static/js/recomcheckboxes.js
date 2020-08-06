/* recomcheckboxes.js for createnew.html and changenew.html

Maurice Kingma
Minor Programmeren - Web App Studio

Javascript for disabling checkboxes when input
*/

function disable() {
    for (var i = 0; i < doublesCheckboxes.length; i++) {
        if (doublesCheckboxes[i].checked == false && !(doublesCheckboxes[i].hasAttribute("disabled")) && !(doublesCheckboxes[i].hasAttribute("notdisabled"))) {
            doublesCheckboxes[i].setAttribute("disabled", "true");
        } else if (doublesCheckboxes[i].checked == false && doublesCheckboxes[i].hasAttribute("disabled")) {
            doublesCheckboxes[i].removeAttribute('disabled');
        } else if (doublesCheckboxes[i].checked) {
            doublesCheckboxes[i].setAttribute("notdisabled", "none");
        } else {
            doublesCheckboxes[i].removeAttribute('notdisabled');
        };
    };
    for (var j = 0; j < doublesCheckboxes.length; j++) {
        if (doublesCheckboxes[j].checked) {
            document.querySelector('#sameRec').removeAttribute("disabled")
            break
        } else {
            document.querySelector('#sameRec').setAttribute("disabled", "true")
        }
    };
};

document.addEventListener('DOMContentLoaded', () => {
    doublesCheckboxes = document.querySelectorAll('[onchange="disable()"]');
    for (var k = 0; k < doublesCheckboxes.length; k++) {
        if (doublesCheckboxes[k].checked) {
            disable()
            break
        }
    }
});
