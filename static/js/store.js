var page = 1;
var mpage = 2;
var sorting = '';
var category_ids = new Array();
var coupon_types = new Array();
var is_new = false;
var is_tranding = false;
var is_sticky = false;
var deal_type_filters_active = false;
var current_url = window.location.href;
$(function() {
	if ($('.index-container').length > 0) {
		init_sticky_header();
	}
	else {
		$('.header').removeClass('hidden');
		$('.header').addClass('top-search');
		$('.header').addClass('fixed-container');
		$('.menu-row').addClass('top-menu');
		$('.menu-row').addClass('bottom-shadow');
		$('.menu-row').addClass('fixed-container');
		$('.menu-row').removeClass('sticky');
		$('.prescroll-header').addClass('hidden');
		$('.top-header').removeClass('sticky');
		$('.top-header').addClass('fixed-container');
	}
	fetch_items(reset_items=true);

	$(window).bind('hashchange', function(e) { 
		var coupon_id = window.location.hash.substr(2, window.location.hash.length);
		if (coupon_id) {
			load_coupon(coupon_id);
		}
	});
	
	var coupon_id = $('.coupons').attr('id');
	if (coupon_id) {
		load_coupon(coupon_id);
	}

	$('.sorting-item a').click(function(){
		$('.sorting-item').removeClass('selected-sorting');
		$(this).parent().addClass('selected-sorting');
		sorting = $(this).attr('class');
		fetch_items(reset_items=true);
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
			if (deal_type_filters_active) {
				$(this).addClass('selected');
				$(this).find('.filter-icon').addClass('selected');
				$(this).find('.filter-icon').append('<a href="javascript:void(null);" class="close-tag"><img src="/static/img/close_tag.png"></a>');
			}
			else {
				$(this).addClass('selected');
				$(this).find('.filter-icon').addClass('selected');
				$(this).find('.filter-icon').append('<a href="javascript:void(null);" class="close-tag"><img src="/static/img/close_tag.png"></a>');
				$('.filter-container').each(function() {
					if ($(this).attr('id') != coupon_type) {
						$(this).removeClass('selected');
						$(this).children().removeClass('selected');
						$(this).find('a').remove();
					}
				});
				deal_type_filters_active = true;
			}
		}
		else {
			coupon_types.splice(coupon_types.indexOf(coupon_type),1);
			$(this).removeClass('selected');
			$(this).children().removeClass('selected');
			$(this).find('a').remove();
		}
		fetch_items(reset_items=true);
	});
	
	$('.category a').live('click', function() {
		var category_id = $(this).attr('id');
		category_ids.push(category_id);
		$(this).parent().removeClass('category');
		$(this).parent().addClass('current-category');
		$(this).after('<a href="javascript:void(null)" class="close-category"><img src="/static/img/close_category.png"></a>');
		sorting = $(this).attr('class');
		fetch_items(reset_items=true);
	});
	
	$('.close-category').live('click', function() {
		var category_id = $(this).attr('id');
		category_ids.splice(category_ids.indexOf(category_id),1);
		$(this).parent().removeClass('current-category');
		$(this).parent().addClass('category');
		$(this).remove();
		sorting = $(this).attr('class');
		fetch_items(reset_items=true);
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
		$('.index-labels a').removeClass('active');
		var filter_type = $(this).attr('id');
		if (filter_type != 'coupon_type') {
			$(this).addClass('active');
			if (filter_type == 'new') {
				is_new = true;
				is_tranding = false;
			}
			else {
				is_tranding = true;
				is_new = false;
			}
			fetch_items(reset_items=true);
		}
	});
	$('.coupon-type li').click(function() {
		var coupon_type = $(this).attr('id');
		$('.coupon-type li').removeClass('active');
		$(this).addClass('active');
	});
	
	if ($('.search-merchants-container').length > 0) {
		var citems = $('.search-carousel').find('li').length;
		var start = citems - 5;
		var limit = citems - 1;
		if ($('.search-carousel').find('li').length > 5) {
			$('.search-carousel').jcarousel({
			  	vertical: true
			});
			$('.prev').click(function() {
				$('.search-carousel').jcarousel('scroll', '+=1');
			});
			$('.next').click(function() {
				$('.search-carousel').jcarousel('scroll', '-=1');
			});
			$('.search-carousel').on('jcarousel:visiblein', 'li:eq('+limit+')', function(event, carousel) {
			    fetch_merchants();
			});
		}
		else {
			$('.prev').hide();
			$('.next').hide();
		}
	}
	
	$('#subscribe-link').click(function(){
		$('.subscription-popup').show();
		$('.overlay').show();
		$('.prescroll-header').waypoint('disable');
		$('.more-coupons').waypoint('disable');
	});
	
	$('#close-subscription-popup').click(function() {
		$('.subscription-popup').hide();
		$('.overlay').hide();
		$('.prescroll-header').waypoint('enable');
		$('.more-coupons').waypoint('enable');
	});
	
    $(window).keyup(function(e){
	    if(e.keyCode === 27) {
    	    close_popups();
		}
	});
	
	$('.overlay').click(function() {
		close_popups();
	});
	
	$('#subscribe-form').submit(function() {
		$('#subscribe-form').ajaxSubmit({'success': subscribe_form_callback, 'dataType': 'json'});
		return false;
	});
	
	$('.coupon-subscribe-form').live('submit', function() {
		$(this).ajaxSubmit({'success': coupon_subscribe_form_callback, 'dataType': 'json'});
		return false;
	});
	
	$('.use-coupon').live('click', function(e) {
		var coupon_id = $(this).attr('id');
		load_coupon(coupon_id);
		return false;
	});
	$('.top-coupon-types a').mouseover(function() {
		var coupon_type_id = $(this).attr('id').substr(3, $(this).attr('id').length);
		$('.top-popular-coupon').addClass('hidden');
		$('#pc-' + coupon_type_id).removeClass('hidden');
		$('.top-featured-section').addClass('hidden');
		$('#fc-' + coupon_type_id).removeClass('hidden');
		$('.top-store').addClass('hidden');
		$('#st-' + coupon_type_id).removeClass('hidden');
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
}
function render_coupons(data, reset_items) {
	var count = 0;
	var coupons_limit = 3;
	if ($('.main-rail').hasClass('landing-rail')) {
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
										<a href="{{ merchant_link }}" target="_blank" class="merchant-link"> \
											<img src="{{ image }}"> \
										</a> \
									</div> \
									<div class="use-coupon" id="{{ id }}"> \
										Use Coupon \
									</div> \
									<div class="coupon-bottom"> \
										<div class="coupon-right-bottom"> \
											Share \
											<a href="{{ facebook_share_url }}"><img src="/static/img/facebook_share_icon.png"></a> \
											<a href="{{ twitter_share_url }}""><img src="/static/img/twitter_share_icon.png"></a> \
											<a href="mailto:?body={{ email_share_url }}"><img src="/static/img/email_share_icon.png"></a> \
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
	data.email_share_url = function() {
		return encodeURIComponent(this.full_success_path);
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
		else if (this.coupon_type == 'gift') {
			return '<div class="coupon-left-label freebies-label"> \
						<img src="/static/img/freebies_icon.png">Freebies \
					</div>';
		}
	};
	html = Mustache.to_html(template, data);
	$('.prescroll-header').waypoint('disable');
	if (reset_items) {
		$('.coupons').html(html);
	}
	else {
		$('.coupons').append(html);
	}
	$('.prescroll-header').waypoint('enable');
	init_waypoint();
}

function render_merchants(data) {
	template = '{{#items}} \
						<li class="search-merchant-container newmerchant"> \
							<a href="{{ local_path }}"><img src="{{ image }}"></a> \
						</li> \
				{{/items}}';
	html = Mustache.to_html(template, data);
	$('.search-merchant-container').last().after(html);
	$('.search-carousel').jcarousel('reload', {
    	vertical: true,
	});
	var limit = $('.search-carousel').find('li').length - 1;
	$('.search-carousel').off('jcarousel:visiblein');
	$('.search-carousel').on('jcarousel:visiblein', 'li:eq('+limit+')', function(event, carousel) {
		fetch_merchants();
	});
}

function init_waypoint() {
	$('.more-coupons').waypoint('destroy');
	$('.more-coupons').waypoint(function(direction) {
		$('.main-row span').html($(this).oldScroll);
		if (direction === 'down') {
			fetch_items(reset_items=false);
		}
	}, {
		offset: function() {
			return $(window).height() * 1.5 - $(this).outerHeight();
		},
	});
}

function fetch_items(reset_items) {
	var url = window.location.pathname;
	var parameters = new Array();
	var i = 0;
	var q = $('input[name=q]').val();
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
	if (q) {
		parameters['q'] = q;
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
			init_waypoint();
		}
	}, 'json');
}

function fetch_merchants() {
	var url = window.location.pathname;
	var parameters = new Array();
	var i = 0;
	var q = $('input[name=q]').val();
	if (mpage > 1) { 
		url += 'page/' + mpage + '/';
	}
	if (q) {
		parameters['q'] = q;
	}
	parameters['fetch_merchants'] = true;
	for (key in parameters) {
		var value = parameters[key];
		if (i == 0) {
			url += '?';
		}
		else {
			url += '&';
		}
			url += key + '=' + value;
		i++;
	}
	$.get(url, function(data) {
		render_merchants(data);
		mpage += 1;
	}, 'json');
}

function init_sticky_header() {
	$('.prescroll-header').waypoint({
		  offset: function() {
		    return -$(this).height() + 55;
		  },
		  handler: function(direction) {
				if (direction === 'down') {
					$('.header').removeClass('hidden');
					$('.header').addClass('sticky top-search');
					$('.menu-row').addClass('top-menu');
					$('.menu-row').addClass('bottom-shadow');
					$('.prescroll-header').addClass('hidden');
					/*if (!is_sticky) {
						init_waypoint();
						is_sticky = true;
					}*/
				}
				else if (direction == 'up') {
					$('.header').addClass('hidden');
					$('.header').removeClass('sticky top-search');
					$('.menu-row').removeClass('top-menu');
					$('.menu-row').removeClass('bottom-shadow');
					$('.prescroll-header').removeClass('hidden');
				}
			}, 
	});
}

function subscribe_form_callback(response, statusText, xhr, $form) {
	$('#subscribe-form').find('span, br').remove();
	if (!response.success && typeof(response.errors) != 'undefined') {
		for (key in response.errors) {
			$('#subscribe-form').find('input[name='+key+']').before('<span>'+response.errors[key]+'</span><br><br>');
		}
	}
	if (response.success) {
		$('.subscription-popup-right').html('<span>You have been subscribed. <img src="/static/img/check_icon.png"></span>');
	}
}

function coupon_subscribe_form_callback(response, statusText, xhr, $form) {
	if (!response.success && typeof(response.errors) != 'undefined') {
		for (key in response.errors) {
			var field = $form.find('input[name='+key+']');
			field.attr('title', response.errors[key]);
			field.tipsy({trigger: 'manual', gravity: 'sw', opacity: 1});
			field.tipsy('show');
		}
	}
	if (response.success) {
		$('.subscription-popup-right').html('<span>You have been subscribed. <img src="/static/img/check_icon.png"></span>');
	}
}

function load_coupon(coupon_id) {
	$.get('/o/'+coupon_id, function(data) {
			render_coupon_popup(data, coupon_id);
			$('.overlay').show();
			var state_obj = {'coupon_id': coupon_id};
			history.pushState(state_obj, "Coupon Page", data.local_path);
	}, 'json');
}

function render_coupon_popup(data, coupon_id) {
	data.csrf = $('input[name=csrfmiddlewaretoken]').val();
	data.id = coupon_id;
	var template = '<div class="coupon-popup"> \
						<div class="coupon-popup-header">Coupon code \
							<a href="javascript:close_coupon_popup();"><img src="/static/img/close_coupon.png"></a> \
						</div> \
						{{# code }} \
						<div class="coupon-popup-code"> \
							<input type="text" value="{{ code }}" placeholder="coupon" readonly> \
							<input type="button" id="coupon-code-{{ id }}" value="Click to copy"> \
						</div> \
						{{/ code }} \
						{{^ code }} \
							<div class="coupon-popup-code"> \
								No coupon code required.<br> \
								<input type="button" value="Shop at {{ merchant_name }}"> \
							</div> \
						{{/ code}} \
						<div class="coupon-popup-body"> \
							<div class="coupon-popup-logo"> \
								<a href="{{ merchant_link }}" target="_blank"> \
									<img src="{{ image }}" class="merchant-logo"> \
								</a> \
							</div> \
							<div class="coupon-popup-description"> \
								<h2 class="short-description">{{ short_desc }}</h2> \
									{{& description }} \
							</div> \
							<br clear="both"> \
							{{# code }} \
								<span><a href="{{ url }}" target="_blank">Shop at {{ merchant_name }} &raquo;</a></span> \
							{{/ code }} \
						</div> \
							<div class="coupon-popup-bottom"> \
								Should we notify you when we add new coupons and deals for Store?<br> \
								<form action="/e/subscribe/" method="post" class="coupon-subscribe-form"> \
									<input type="hidden" name="csrfmiddlewaretoken" value="{{ csrf }}"> \
									<input type="text" name="email" placeholder="Email address" value=""> \
									<input type="submit" value="Let me know"> \
								</form> \
							</div> \
					</div>';
	html = Mustache.to_html(template, data);
	$('.subscription-popup').after(html);
	init_clipboard($('#coupon-code-' + coupon_id));
}

function close_coupon_popup() {
	$('.coupon-popup').hide();
	$('.overlay').hide();
	$('.prescroll-header').waypoint('enable');
}

function close_popups() {
	$('.subscription-popup').hide();
	$('.coupon-popup').hide();
	$('.overlay').hide();
	$('.tipsy').remove();
	$('.prescroll-header').waypoint('enable');
	var state_obj = {'coupon_id': null};
	history.pushState(state_obj, "Coupon Page", current_url);
}

function init_clipboard(element) {
    element.clipboard({
        path: '/static/js/jquery.clipboard.swf',
        copy: function() {
        	var text_input = element.parent().find('input[type=text]');
        	text_input.attr('title', 'Copied!');
			text_input.tipsy({trigger: 'manual', gravity: 'sw', opacity: 1});
			text_input.tipsy('show');
            return text_input.val();
        }
    });
}
