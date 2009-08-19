;$(document).ready(function() {
	$('.basket:submit').click(function(){
		if ($(this).siblings('select.metaitem').size()) {
			var item_id = $(this).siblings('select.metaitem').attr('value');
		} else {
			var item_id = $(this).attr('id').split('item-')[1];
		}
		add_to_basket(item_id);
	});
	
	$('#refresh').click(function() {
		$(this).after('<input type="hidden" name="ajax" value="1">');
	});


});

function add_to_basket(item_id) {
	$.post('/basket/add/', {'item': item_id}, function (){
		reload_basket();
	});
}

function reload_basket() {
	var loading_div = $('.loading').clone();
	$('#basket_panel p').prepend(loading_div);
	loading_div.show();
	$('#basket_panel').load('/basket/ajax/', null, function(){
		loading_div.hide();
	});
}
