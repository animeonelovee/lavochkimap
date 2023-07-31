$(function() {
	var pull = $('#pull');
		menu = $('#nav-m');
        space = $('#space');

	$(pull).on('click', function(e) {
		e.preventDefault();
		menu.toggle();
        space.toggle();
	});
    $(window).resize(function(){
        var w = window.innerWidth;
        if(w > 960) {
        	menu.removeAttr('style');
            space.removeAttr('style');
        }
    });
});