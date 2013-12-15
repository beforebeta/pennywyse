var page = 2;
var sorting = '';
var category_ids = new Array();
var coupon_types = new Array();
var is_new = false;
var is_tranding = false;
$(function() {
	init_waypoint();
	$('.sorting-item a').click(function(){
		$('.sorting-item').removeClass('selected-sorting');
		$(this).parent().addClass('selected-sorting');
		sorting = $(this).attr('class');
		fetch_items(reset_items=true);
		init_waypoint();
	});
	$('.more-categories a').click(function() {
		$('.more-categories').remove();
		$('.category').each(function() {
			if ($(this).hasClass('hidden')) {
				$(this).removeClass('hidden');
			}
		});
	});
	$('.filter-container').live('click', function() {
		var coupon_type = $(this).attr('id');
		if (!$(this).hasClass('selected')) {
			coupon_types.push(coupon_type);
			$(this).addClass('selected');
			$(this).find('.filter-icon').addClass('selected');
			$(this).find('.filter-icon').append('<a href="javascript:void(null);" class="close-tag"><img src="/static/img/close_tag.png"></a>');
		}
		else {
			coupon_types.splice(coupon_types.indexOf(coupon_type),1);
			$(this).removeClass('selected');
			$(this).children().removeClass('selected');
			$(this).find('a').remove();
		}
		fetch_items(reset_items=true);
		init_waypoint();
	});
	$('.category a').live('click', function() {
		var category_id = $(this).attr('id');
		category_ids.push(category_id);
		$(this).parent().removeClass('category');
		$(this).parent().addClass('current-category');
		$(this).after('<a href="javascript:void(null)" class="close-category"><img src="/static/img/close_category.png"></a>');
		sorting = $(this).attr('class');
		fetch_items(reset_items=true);
		init_waypoint();
	});
	$('.close-category').live('click', function() {
		var category_id = $(this).attr('id');
		category_ids.splice(category_ids.indexOf(category_id),1);
		$(this).parent().removeClass('current-category');
		$(this).parent().addClass('category');
		$(this).remove();
		sorting = $(this).attr('class');
		fetch_items(reset_items=true);
		init_waypoint();
	});
	$('.coupon-container').live('mouseover', function() {
		if (!$(this).hasClass('coupon-banner')) {
			$(this).find('.use-coupon').show();
		}
	});
	$('.coupon-container').live('mouseout', function() {
		if (!$(this).hasClass('coupon-banner')) {
			$(this).find('.use-coupon').hide();
		}
	});
	$('.index-labels a').click(function() {
		var filter_type = $(this).attr('id');
		if (filter_type == 'new') {
			is_new = true;
			is_tranding = false;
		}
		else {
			is_tranding = true;
			is_new = false;
		}
		fetch_items(reset_items=true);
		init_waypoint();
	});
});
function select_categories(criteria) {
	if (criteria == 'all') {
		$('.category').each(function() {
			$(this).removeClass('category');
			$(this).addClass('current-category');
			$(this).find('a').after('<a href="#" class="close-category"><img src="/static/img/close_category.png"></a>');
		});
	}
	else {
		$('.current-category').each(function() {
			$(this).removeClass('current-category');
			$(this).addClass('category');
			$(this).find('.close-category').remove();
		});
		category_ids = [];
	}
	fetch_items(reset_items=true);
	init_waypoint();
}
function select_filters(criteria) {
	if (criteria == 'all') {
		$('.filter-container').each(function() {
			$(this).addClass('selected');
			$(this).find('.filter-icon').addClass('selected');
			$(this).find('.filter-icon').append('<a href="javascript:void(null);" class="close-tag"><img src="/static/img/close_tag.png"></a>');
			var coupon_type = $(this).attr('id');
			coupon_types.push(coupon_type);
		});
	}
	else {
		$('.filter-container').each(function() {
			$(this).removeClass('selected');
			$(this).find('.filter-icon').removeClass('selected');
			$(this).find('.close-tag').remove();
		});
		coupon_types = [];
	}
	fetch_items(reset_items=true);
	init_waypoint();
}
function render_coupons(data, reset_items) {
	var count = 0;
	var coupons_limit = 3;
	if ($('.main-rail').hasClass('index-rail')) {
		coupons_limit = 4;
	}
	template = '{{#items}} \
						<div class="coupon-container {{#count}}coupon-last{{/count}}"> \
						<div class="coupon-body"> \
							<div class="coupon-header"> \
								{{& coupon_type_container }} \
							</div> \
							<hr> \
							<h1 class="short-description">{{ short_desc }}</h1> \
							{{ description }}<br> \
										<span class="ends">Ends {{ end }}</span> \
										<div class="description">{{#image}}<img src="{{ image }}">{{/image}} \
										</div> \
									</div> \
									<div class="use-coupon"> \
										<a href="{{ full_success_path}}">Use Coupon</a> \
									</div> \
									<div class="coupon-bottom"> \
										<div class="coupon-right-bottom"> \
											Share \
											<a href="{{ facebook_share_url }}"><img src="/static/img/facebook_share_icon.png"></a> \
											<a href="{{ twitter_share_url }}""><img src="/static/img/twitter_share_icon.png"></a> \
											<a href="#"><img src="/static/img/email_share_icon.png"></a> \
										</div> \
									</div> \
								</div> \
				{{/items}}<br clear="both">';
	data.count = function () {
    	count++;
    	if (count % coupons_limit == 0) {
    		return true;
    	}
    	return false;
   	};
   	data.facebook_share_url = function() {
   		return 'https://www.facebook.com/sharer/sharer.php?u=' + encodeURIComponent(this.full_success_path);
   	};
   	data.twitter_share_url = function() {
   		return 'https://twitter.com/share?url=' + encodeURIComponent(this.full_success_path);
	};
	data.coupon_type_container = function() {
		if (this.coupon_type == 'free_shipping') {
			return 	'<div class="coupon-left-label free-shipping-label"> \
						<img src="/static/img/free_shipping_icon.png">Free Shipping \
					</div>';
		}
		else if (this.coupon_type == 'on_sale') {
			return '<div class="coupon-left-label on-sale-label"> \
						<img src="/static/img/on_sale_icon.png">On Sale \
					</div>';
		}
		else if (this.coupon_type == 'groceries') {
			return '<div class="coupon-left-label groceries-label"> \
						<img src="/static/img/groceries_icon.png">Groceries \
					</div>';
		}
		else if (this.coupon_type == 'coupon') {
			return '<div class="coupon-left-label coupon-code-label"> \
						<img src="/static/img/coupon_code_icon.png">Coupon \
					</div>';
		}
		else if (this.coupon_type == 'printable') {
			return '<div class="coupon-left-label printable-label"> \
						<img src="/static/img/printable_icon.png">Printables \
					</div>';
		}
	};
	html = Mustache.to_html(template, data);
	if (reset_items) {
		$('.coupons').html(html);
	}
	else {
		$('.coupons').append(html);
	}
}
function init_waypoint() {
	$('.more-coupons').waypoint(function(direction) {
		if (direction === 'down') {
			fetch_items(reset_items=false);
		}
	}, {
		offset: 'bottom-in-view',
	});
}
function fetch_items(reset_items) {
	var url = window.location.pathname;
	var parameters = new Array();
	var i = 0;
	if (reset_items) {
		page = 1;
	}
	if (page > 1) { 
		url += 'page/' + page + '/';
	}
	if (sorting) {
		parameters['sorting'] = sorting;
	}
	if (category_ids.length > 0) {
		parameters['category_id'] = category_ids;
	}
	if (coupon_types.length > 0) {
		parameters['coupon_type'] = coupon_types;
	}
	if (is_new) {
		parameters['is_new'] = is_new;
	}
	if (is_tranding) {
		parameters['is_tranding'] = is_tranding;
	}
	for (key in parameters) {
		var value = parameters[key];
		if (i == 0) {
			url += '?';
		}
		else {
			url += '&';
		}
		if (!$.isArray(value)) {
			url += key + '=' + value;
		}
		else {
			for (j=0;j<value.length;j++) {
				if (j > 0) {
					url += '&';
				}
				url += key + '=' + value[j];
			}
		}
		i++;
	}
	$.get(url, function(data) {
		render_coupons(data, reset_items);
		if (page <= data.total_pages) {
			page += 1;
			$('.more-coupons').waypoint('destroy');
			init_waypoint();
		}
	}, 'json');
}
