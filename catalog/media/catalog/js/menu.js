$(document).ready(function(){
	// раскрытие списков меню
	$('#masterdiv a').click(function(){
		var next = $(this).next();
		if (next.is('ul')) {
			next.toggle();
		}
		if ($(this).attr('href') == '#')
			return false;
	});
	
	// смена деревьев меню в главном меню
	$('.menuCatalogChange :radio').change(function(){

		var target_id = $(this).attr('id').split('_')[1];
		$('#masterdiv div[id=topmenu-'+target_id+']').show();
		$('#masterdiv div[id!=topmenu-'+target_id+']').hide();
		$.cookies.set('section', target_id, {
			housToLive: '100',
			path: '/',
			secure: false
		});
	});
});

function expand(li_id) {
	$('#' + li_id).parents().map(function () {
		$(this).show();
	});
}