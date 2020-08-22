/* videoplayer.js for guide.html

Maurice Kingma
Minor Programmeren - Web App Studio

Javascript for displaing video instead of image on front page
*/
function videoplayersetup() {
	if (document.querySelector('.videolink')) {
		if (document.querySelector('.videolink').dataset.link.length > 83) {
			var description = document.querySelector('.description');
			var img = description.querySelector('img');
			img.style.display = "none"
			var videoplayer = document.createElement('div');
			videoplayer.className = "videoplayer"
			videoplayer.style.backgroundImage = 'url("' + img.src + '")'
			videoplayer.style.backgroundSize = "cover"
			var iframe = document.createElement('iframe');
			iframe.src = document.querySelector('.videolink').dataset.link;
			iframe.frameborder = "0"
			iframe.style = "pointer-events: none;";
			iframe.className = "video"
			iframe.setAttribute('allowfullscreen', '');
			videoplayer.appendChild(iframe)
			img.parentNode.insertBefore(videoplayer, img.nextSibling);
			var length = document.querySelector('.videolink').dataset.length
			setTimeout(function() {
				document.querySelector('.video').style.display = "block";
				img.style.display = "none"
			}, 4100);
			setTimeout(function() {
				document.querySelector('.video').style.display = "none";
			}, (length * 1000) - 4000);
		}
	}
}
document.addEventListener('DOMContentLoaded', () => {
	videoplayersetup()
})
