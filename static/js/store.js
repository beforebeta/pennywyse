var page = 2;
var mpage = 2;
var mtotal = 0;
var sorting = '';
var category_ids = new Array();
var coupon_types = new Array();
var coupon_type = '';
var is_sticky = false;
var is_touch = false;
var deal_type_filters_active = false;
var current_url = window.location.href;
var is_mobile = false;
var base_url = window.location.pathname;

$(function() {
	// removing pagination block, to be displayed with disabled JS only 
	$('.pagination').remove();
	
	// enabling sticky header only on landing page and only for desktop pages
	if ($('.landing-container').length > 0 && $(window).width() >= 992) {
		is_sticky = true;
		init_sticky_header();
	}
	else {
		if ($('.index-container').length > 0 && $(window).width() >= 992) {
			$('.header').removeClass('hidden');
			$('.header').addClass('top-search sticky');
			$('.menu-row').addClass('top-menu');
			$('.menu-row').addClass('bottom-shadow');
			$('.prescroll-header').addClass('hidden');
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
	}
	
	if (window.location.hash == '#subscribe') {
		$('.subscription-popup').show();
		$('.overlay').show();
		$('.prescroll-header').waypoint('disable');
		$('.more-coupons').waypoint('disable');
	}
	
	if ('ontouchstart' in window || window.DocumentTouch && document instanceof DocumentTouch) {
		is_touch = true;
	}
		
	// applying styles for mobile layout, if necessary width has been detected
	if ($(window).width() < 992) {
		is_mobile = true;
		$('.main-container').addClass('mobile-container');
		$('.middle-container').addClass('mobile-middle-container');
		$('.index-rail').addClass('mobile-index-rail');
		$('.search-main-rail').addClass('mobile-index-rail');
		$('.main-rail').addClass('mobile-index-rail');
		$('.coupon-container').addClass('mobile-coupon-container');
		$('.coupon-bottom').remove();
	}
	else if (is_touch) {
		$('.use-coupon').addClass('fixed-use-coupon');
	}
	
	$('.expandable').on('click', expandable_select_callback);
	
	$('#mobile-menu').click(function() {
		if ($('.mobile-menu').is(':visible')) {
			$('.mobile-menu').hide('slide', { direction: 'left' }, 250);
		}
		else {
			$('.mobile-menu').show('slide', { direction: 'left' }, 250);
		}
	});
	
	// initializing infinite scroll
	init_waypoint();

	// displaying coupon popup automatically, if coupon ID provided
	var coupon_id = $.url().param('c');
	if (coupon_id) {
		load_coupon(coupon_id);
	}

	$('.sorting-item').click(function(){
		$('.sorting-item').removeClass('selected-sorting');
		$(this).addClass('selected-sorting');
		sorting = $(this).find('a').attr('class');
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
	
	$('.category').live('click', function() {
		var category_id = $(this).find('a').attr('id');
		category_ids.push(category_id);
		$(this).removeClass('category');
		$(this).addClass('current-category');
		$(this).find('a').after('<a href="javascript:void(null)" class="close-category"><img src="/static/img/close_category.png"></a>');
		fetch_items(reset_items=true);
	});
	
	$('.current-category').live('click', function() {
		var category_id = $(this).attr('id');
		category_ids.splice(category_ids.indexOf(category_id),1);
		$(this).removeClass('current-category');
		$(this).addClass('category');
		$(this).find('.close-category').remove();
		fetch_items(reset_items=true);
	});
		
	$('.coupon-container').live('mouseover', function() {
		if (!$(this).hasClass('coupon-banner')) {
			$(this).find('.use-coupon').addClass('use-coupon-visible');
		}
	});
	
	$('.coupon-container').live('mouseout', function() {
		if (!$(this).hasClass('coupon-banner')) {
			$(this).find('.use-coupon').removeClass('use-coupon-visible');
		}
	});
	
	$('#mobile-categories').click(function() {
		if ($('.mobile-category :visible').length > 0) {
			$('.mobile-category').hide();
			$(this).find('.glyphicon').removeClass('glyphicon-chevron-up');
			$(this).find('.glyphicon').addClass('glyphicon-chevron-down');
		}
		else {
			$(this).find('.glyphicon').removeClass('glyphicon-chevron-down');
			$(this).find('.glyphicon').addClass('glyphicon-chevron-up');
			$('.mobile-category').show();
		}
	});
	
	$('#mobile-groceries').click(function() {
		if ($('.mobile-grocery :visible').length > 0) {
			$('.mobile-grocery').hide();
			$(this).find('.glyphicon').removeClass('glyphicon-chevron-up');
			$(this).find('.glyphicon').addClass('glyphicon-chevron-down');
		}
		else {
			$(this).find('.glyphicon').removeClass('glyphicon-chevron-down');
			$(this).find('.glyphicon').addClass('glyphicon-chevron-up');
			$('.mobile-grocery').show();
		}
	});
	
	$('#mobile-subscribe-link').click(function() {
		if ($('.mobile-subscription').is(':visible')) {
			$('.mobile-subscription').hide();
		}
		else {
			$('.mobile-subscription').show();
		}
	});
	
	$('.index-labels a').click(function() {
		$('.index-labels a').removeClass('active');
		var filter_type = $(this).attr('id');
		if (filter_type != 'coupon_type') {
			$(this).addClass('active');
			sorting = filter_type;
			fetch_items(reset_items=true);
		}
	});
	
	if ($('.not-found-container').length > 0) {
		page = 1;
		sorting = 'new';
		base_url = '/';
		fetch_items(reset_items=true);
	}
	
	// switching between "most popular", "featured" and "stores" sections on "top coupons" mobile page
	$('.mobile-index-labels a').click(function() {
		$('.mobile-index-labels a').removeClass('active');
		if ($('.coupon-types').hasClass('expanded')) {
			$('.coupon-types').find('li').removeClass('selected');
			$('.coupon-types').find('li:first').addClass('selected');
			$('.coupon-types').closest('.coupon-types').removeClass('expanded');
			$(this).find('.expanded-choices li').off('click');
			$(this).find('.expanded-choices li').closest('.expandable').on('click', expandable_select_callback);
		}
		
		var filter_type = $(this).attr('id');
		if (filter_type != 'coupon_type') {
			$(this).addClass('active');
		}
		$('.coupon-container').hide();
		$('.top-menu-store').hide();
		if (filter_type == 'most-popular') {
			$('.menu-popular-coupon:first').show();
		}
		else if (filter_type == 'featured-coupons') {
			$('.menu-featured-coupon:first').removeClass('hidden');
			$('.menu-featured-coupon:first').show();
			$('.menu-featured-coupon:first').find('.coupon-container').show();
		}
		else if (filter_type == 'stores') {
			$('.top-menu-store:first').removeClass('hidden');
			$('.top-menu-store:first').show();
		}
	});
	
	$('.coupon-type li').click(function() {
		coupon_type = $(this).attr('id');
		$('.coupon-type li').removeClass('active');
		$(this).addClass('active');
		fetch_items(reset_items=true);
	});
	
	if ($('.search-merchants-container').length > 0) {
		var citems = $('.search-carousel').find('li').length;
		var start = citems - 5;
		var limit = citems - 1;
		$('.next').css('visibility', 'hidden');
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
			$('.search-carousel').on('jcarousel:animateend', function(event, carousel) {
			    var first = $(this).jcarousel('first');
			    var last = $(this).jcarousel('last');
			    var lastIndex = $(this).jcarousel('items').index(last);
			    var firstIndex = $(this).jcarousel('items').index(first);
			    var total = $(this).jcarousel('items').size();
			
			    if (lastIndex == (total - 1)) {
			    	$('.prev').css('visibility', 'hidden');
			    }
			    else {
			    	$('.prev').css('visibility', 'visible');
			    }
			    if (firstIndex == 0) {
			    	$('.next').css('visibility', 'hidden');
			    }
			    else {
			    	$('.next').css('visibility', 'visible');
			    }
			});
		}
		else {
			$('.prev').css('visibility', 'hidden');
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
	
	$('.subscribe-form').submit(function() {
		data = {csrfmiddlewaretoken: $.cookie('csrftoken')};
		$(this).ajaxSubmit({'success': subscribe_form_callback, 'dataType': 'json', 'data': data});
		return false;
	});
	
	$('.coupon-subscribe-form').live('submit', function() {
		data = {csrfmiddlewaretoken: $.cookie('csrftoken')};
		$(this).ajaxSubmit({'success': coupon_subscribe_form_callback, 'dataType': 'json', 'data': data});
		return false;
	});
	
	$('.use-coupon, .coupon-top-body').live('click', function(e) {
		var coupon_id = $(this).attr('id');
		window.location = '/s/' + coupon_id + '/';
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

	$('.top-coupons-link').click(function() {
		window.location = '/top-coupons/';
	});

	$('.right-mobile-rail .filter').click(function() {
		if (!$('.mobile-filters').is(':visible')) {
			$('.mobile-filters').removeClass('hidden');
		}
		else {
			$('.mobile-filters').addClass('hidden');
		}
	});

	$(".coupon-description").dotdotdot({
		ellipsis: '... ',
 		wrap: 'letter',
 		fallbackToLetter: true,
 		after: null,
 		watch: false,
		height: null,
		tolerance: 0,
		callback: function( isTruncated, orgContent ) {
			$(this).addClass('truncated');
		},
	});
	
	$('.top-coupon-types a').mouseover(function() {
		$('.top-coupon-types a').removeClass('top-coupon-active');
		$(this).addClass('top-coupon-active');
	});
	
	if ($('.no-search-results').length > 0 || $('.no-results').length > 0) {
		base_url = '/';
		fetch_items(reset_items=true);
	}
	
	$('.menu-item').mouseover(function() {
		$('.menu-item').find('.menu-link').removeClass('active-dropdown-link');
		$('.active-dropdown-item').hide();
		$('.menu-item').find('ul').removeClass('active-dropdown-item');
		$(this).find('ul').addClass('active-dropdown-item');
		$(this).find('.menu-link').addClass('active-dropdown-link');
	});
	
	$('.main-dropdown-section').mouseover(function() {
		$('.active-dropdown-item').show();
	});
	$('.active-dropdown-item').live('mouseout', function(){
		$(this).hide();
		$('.menu-item').find('.menu-link').removeClass('active-dropdown-link');
	});
	
	$('.facebook-share-url').live('click', function() {
		return !window.open(this.href, 'Share on Facebook', 'width=600,height=300');
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
			var current_coupon_type = $(this).attr('id');
			coupon_types.push(current_coupon_type);
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
	var template = '{{#items}} \
					<div class="coupon-container {{# is_mobile}}mobile-coupon-container{{/is_mobile}}"> \
						<div class="coupon-body"> \
							<a class="coupon-top-body" id="{{ id }}" href="{{ full_success_path}}" target="_blank"> \
								<div class="coupon-header"> \
									<div class="coupon-left-label"> \
										{{& coupon_type_container }} \
									</div> \
								</div> \
								<hr> \
								<h2 class="short-description">{{ short_desc }}</h2> \
								<div class="coupon-description"> \
									{{ description }} \
								</div> \
								{{# end }} \
									<span class="ends">Ends {{ end }}</span> \
								{{/end}} \
							</a> \
							{{# is_company_coupon }} \
								<span class="merchant-link"> \
									<img src="{{ image }}"> \
								</span> \
							{{/is_company_coupon }} \
							{{^ is_company_coupon }} \
								<a href="{{ merchant_link }}" target="_blank" class="merchant-link"> \
									<img src="{{ image }}"> \
								</a> \
							{{/is_company_coupon }} \
						</div> \
						<a class="use-coupon" id="{{ id }}" href="{{ full_success_path}}" target="_blank"> \
							Use Coupon \
						</a> \
						{{^ is_mobile }} \
							<div class="coupon-bottom"> \
								<div class="coupon-right-bottom"> \
									Share \
									<a href="{{ facebook_share_url }}" class="facebook-share-url"><img src="/static/img/facebook_share_icon.png"></a> \
									<a href="{{ twitter_share_url }}""><img src="/static/img/twitter_share_icon.png"></a> \
									<a href="mailto:?body={{ email_share_url }}"><img src="/static/img/email_share_icon.png"></a> \
								</div> \
							</div> \
						{{/is_mobile}} \
					</div> \
				{{/items}}<br clear="both">';
   	data.is_mobile = is_mobile;
   	data.is_company_coupon = $('.coupons').hasClass('company-coupons');
   	data.facebook_share_url = function() {
   		return 'https://www.facebook.com/sharer/sharer.php?u=' + encodeURIComponent(this.full_success_path);
   	};
	data.email_share_url = function() {
		return encodeURIComponent(this.full_success_path);
	};
	data.coupon_type_container = function() {
		if (this.coupon_type == 'free_shipping') {
			return 	'<img src="/static/img/free_shipping_icon.png">Free Shipping';
		}
		else if (this.coupon_type == 'onsale') {
			return '<img src="/static/img/on_sale_icon.png">On Sale';
		}
		else if (this.coupon_type == 'groceries') {
			return '<img src="/static/img/groceries_icon.png">Groceries';
		}
		else if (this.coupon_type == 'coupon_code') {
			return '<img src="/static/img/coupon_code_icon.png">Coupon';
		}
		else if (this.coupon_type == 'printable') {
			return '<img src="/static/img/printable_icon.png">Printables';
		}
		else if (this.coupon_type == 'freebies') {
			return '<img src="/static/img/freebies_icon.png">Freebies';
		}
	};
	
	html =  Mustache.to_html(template, data);
	$('.more-coupons').find('br').remove();
	$('.prescroll-header').waypoint('disable');
	$('.merchant-right span').html(data.total_items);
	if (reset_items) {
		$('.coupons').html(html);
	}
	else {
		$('.coupons').append(html);
	}
	$('.coupon-description:not(.truncated)').dotdotdot({
		ellipsis: '... ',
 		wrap: 'letter',
 		fallbackToLetter: true,
 		after: null,
 		watch: false,
		height: null,
		tolerance: 0,
		callback: function( isTruncated, orgContent ) {
			$(this).addClass('truncated');
		},
	});
	init_sticky_header();
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
			return $(window).height() * 1.7 - $(this).outerHeight();
		},
	});
}

function fetch_items(reset_items) {
	if (!is_mobile) {
		NProgress.configure({ minimum: 0.1 });
		NProgress.start();
	}
	var url = base_url;
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
	if (coupon_type) {
		parameters['coupon_type'] = coupon_type;
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
		if (!is_mobile) {
			NProgress.inc();
		}
		render_coupons(data, reset_items);
		if (page < data.total_pages) {
			page += 1;
			init_waypoint();
		}
		else {
			$('.more-coupons').waypoint('disable');
		}
		if (!is_mobile) {
			NProgress.done();
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
		mtotal = data.total;
	}, 'json');
}

function init_sticky_header() {
	if (is_sticky) {
		$('.prescroll-header').waypoint('destroy');
		$('.prescroll-header').waypoint({
			  offset: function() {
			    return $(this).offset().top - 230;
			  },
			  handler: function(direction) {
					if (direction === 'down') {
						$('.header').removeClass('hidden');
						$('.header').addClass('sticky top-search');
						$('.menu-row').addClass('top-menu');
						$('.menu-row').addClass('bottom-shadow');
						$('.prescroll-header').addClass('hidden');
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
}

function subscribe_form_callback(response, statusText, xhr, $form) {
	$form.find('span, br').remove();
	if (!response.success && typeof(response.errors) != 'undefined') {
		for (key in response.errors) {
			html = '<span>'+response.errors[key]+'</span>';
			if (!is_mobile) {
				html += '<br><br>';
			}
			$form.find('input[name='+key+']').before(html);
		}
	}
	if (response.success) {
		if (is_mobile) {
			$('.mobile-subscription').hide();
			$('.mobile-subscription-ok').remove();
			$('body').append('<div class="mobile-subscription-ok">Got it<br><span class="glyphicon glyphicon-ok"></span></div>');
			$('.mobile-subscription-ok').fadeIn();
			setTimeout(1000);
			$('.mobile-subscription-ok').fadeOut();
		}
		else {
			$('.subscription-popup-right').html('<span>You have been subscribed. <img src="/static/img/check_icon.png"></span>');
		}
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
		var field = $form.find('input[name=email]');
		field.attr('title', 'You have been subscribed.');
		field.tipsy({trigger: 'manual', gravity: 'sw', opacity: 1});
		field.tipsy('show');
	}
}

function load_coupon(coupon_id) {
	$.get('/o/'+coupon_id, function(data) {
			render_coupon_popup(data, coupon_id);
			if (is_mobile) {
				$('.overlay').addClass('mobile-overlay');
			}
			$('.overlay').show();
			var state_obj = {'coupon_id': coupon_id};
			history.pushState(state_obj, "Coupon Page", data.local_path);
	}, 'json');
}

function render_coupon_popup(data, coupon_id) {
	data.csrf = $.cookie('csrftoken');
	data.id = coupon_id;
	data.is_mobile = is_mobile;
	data.facebook_share_url = function() {
   		return 'https://m.facebook.com/sharer/sharer.php?u=' + encodeURIComponent(this.full_success_path);
   	};
	data.email_share_url = function() {
		return encodeURIComponent(this.full_success_path);
	};
	var template = '<div class="coupon-popup {{# is_mobile }}mobile-coupon-popup{{/is_mobile}}" data-href="{{ url }}"> \
						<div class="coupon-popup-header"> \
							{{# is_mobile }} \
								<a href="javascript:close_coupon_popup();">back</a> \
							{{ /is_mobile }} \
							Coupon code \
							{{^ is_mobile}} \
								<a href="javascript:close_coupon_popup();"><img src="/static/img/close_coupon.png"></a> \
							{{/is_mobile}} \
						</div> \
						{{# is_mobile}}<div class="mobile-coupon-body">{{/is_mobile}} \
						{{# code }} \
						<div class="coupon-popup-code"> \
							<input type="text" value="{{ code }}" placeholder="coupon" readonly> \
							{{^is_mobile}} \
								<input type="button" id="coupon-code-{{ id }}" value="Click to copy"> \
							{{/is_mobile}} \
							{{#is_mobile}} \
								<a href="{{ url }}" target="_blank"  class="merchant-button">Shop at {{ merchant_name }}"</a> \
							{{/is_mobile}} \
						</div> \
						{{/ code }} \
						{{^ code }} \
							<div class="coupon-popup-code"> \
								<span>No coupon code required.</span> \
								<a href="{{ url }}" target="_blank"  class="merchant-button">Shop at {{ merchant_name }}</a> \
							</div> \
						{{/ code}} \
						<div class="coupon-popup-body"> \
							<div class="coupon-popup-logo"> \
								<a href="{{ merchant_link }}" target="_blank"> \
									<img src="{{ image }}" class="merchant-logo"> \
								</a> \
							</div> \
							{{# is_mobile }} \
								<a href="#"><h2 class="short-description">{{ short_desc }}</h2></a> \
								<span class="coupon-description">{{& description }}</span> \
								{{# code }} \
									<br clear="both"><a href="{{ url }}" target="_blank">Shop at {{ merchant_name }} &raquo;</a> \
								{{/ code }} \
								\
							{{/is_mobile}} \
							{{^is_mobile}} \
								<div class="coupon-popup-description"> \
									<h2 class="short-description">{{ short_desc }}</h2> \
									<div class="coupon-description">{{& description }}</div> \
									{{# code }} \
										<br clear="both""><a href="{{ url }}" target="_blank">Shop at {{ merchant_name }} &raquo;</a> \
									{{/ code }} \
								</div> \
							{{/is_mobile}} \
							\
							<br clear="both"> \
						</div> \
							<div class="coupon-popup-bottom"> \
								<div class="coupon-popup-subscribe"> \
									{{# is_mobile }} \
									 	Notify me when {{ merchant_name }} has new coupons \
									{{/is_mobile}} \
									{{^ is_mobile }} \
										Should we notify you when we add new coupons and deals for {{ merchant_name }}?<br> \
									{{/is_mobile}} \
									<form action="/e/subscribe/" method="post" class="coupon-subscribe-form"> \
										<input type="hidden" name="csrfmiddlewaretoken" value="{{ csrf }}"> \
										<input type="text" name="email" placeholder="Email address" value=""> \
										{{^ is_mobile }} \
											<input type="submit" value="Let me know"> \
										{{/is_mobile}} \
										{{#is_mobile}} \
										  <button>let me<br>know</button> \
										<br clear="both"> \
										{{/is_mobile}} \
									</form> \
								</div> \
							</div> \
							{{# is_mobile }} \
								<div class="mobile-share-bottom"> \
									<div class="mobile-share-main"> \
										<span>Share this coupon:</span> \
										<div class="mobile-share-right"> \
											<a href="{{ facebook_share_url }}" class="facebook-share-url"><img src="/static/img/mobile_facebook_icon.png"></a> \
											<a href="{{ twitter_share_url }}""><img src="/static/img/mobile_twitter_icon.png"></a> \
											<a href="mailto:?body={{ email_share_url }}"><img src="/static/img/mobile_email_icon.png"></a> \
										</div> \
									</div> \
								</div> \
							{{/is_mobile}} \
							{{# is_mobile}}</div>{{/is_mobile}} \
					</div>';
	html = Mustache.to_html(template, data);
	$('.subscription-popup').after(html);
	if (is_mobile) {
		$('.mobile-container').addClass('fixed');
	}
	$(".coupon-description").dotdotdot({
		ellipsis: '... ',
 		wrap: 'letter',
 		fallbackToLetter: true,
 		after: null,
 		watch: false,
		height: null,
		tolerance: 0,
		callback: function( isTruncated, orgContent ) {
			$(this).addClass('truncated');
		},
	});
	init_clipboard($('#coupon-code-' + coupon_id));
	$('.merchant-button').on('click', merchant_button_callback);
}

function close_coupon_popup() {
	$('.coupon-popup').hide();
	$('.overlay').hide();
	$('.prescroll-header').waypoint('enable');
	$('.tipsy').remove();
	if (is_mobile) {
		$('.mobile-container').removeClass('fixed');
	}
	var state_obj = {'coupon_id': null};
	history.pushState(state_obj, "Coupon Page", current_url);
}

function close_popups() {
	$('.subscription-popup').hide();
	$('.coupon-popup').remove();
	$('.overlay').hide();
	$('.tipsy').remove();
	$('.prescroll-header').waypoint('enable');
	var state_obj = {'coupon_id': null};
	history.pushState(state_obj, "Coupon Page", current_url);
	$('.merchant-button').off('click');
}

function init_clipboard(element) {
    if ($.browser.msie) {
    	element.click(function(){
    		var text_input = element.parent().find('input[type=text]');
    		text_input.attr('title', 'Copied!');
			text_input.tipsy({trigger: 'manual', gravity: 'sw', opacity: 1});
			text_input.tipsy('show');
    		window.clipboardData.setData('Text', text_input.val());
    		var coupon_url = $('.coupon-popup').attr('data-href');
	        track_click(coupon_url, redirect=true);
	        setTimeout(function (){
		    	$('.tipsy').remove();
		    }, 1000);
    	});
    }
    else {
	    element.clipboard({
	        path: '/static/js/jquery.clipboard.swf',
	        copy: function() {
	        	var text_input = element.parent().find('input[type=text]');
	        	text_input.attr('title', 'Copied!');
				text_input.tipsy({trigger: 'manual', gravity: 'sw', opacity: 1});
				text_input.tipsy('show');
	            return text_input.val();
	        },
	        afterCopy: function() {
		       	var coupon_url = $('.coupon-popup').attr('data-href');
	        	track_click(coupon_url, redirect=true);
	        	setTimeout(function (){
		        	$('.tipsy').remove();
		        }, 1000);
	        }
	    });
    }
}

function expandable_callback(event) {
	$(this).parent().find('li').removeClass('selected');
	$(this).addClass('selected');
	$(this).closest('.coupon-types').removeClass('expanded');
	if ($(this).parent().hasClass('coupon-type-select')) {
		coupon_types = new Array($(this).attr('id'));
	}
	if ($(this).parent().hasClass('ordering-select')) {
		sorting = $(this).attr('id');
	}
	if ($(this).parent().hasClass('coupon-type-select') || $(this).parent().hasClass('ordering-select')) {
		fetch_items(reset_items=true);
	}
		
	if ($('.mobile-index-labels').length > 0) {
		var top_coupon_type = $(this).attr('id');
		var coupon_type = $('.mobile-index-labels').find('.active').attr('id');
		if (coupon_type == 'most-popular') {
			$('.menu-popular-coupon').hide();
			$('#mpc-'+top_coupon_type).show();
			$('#mpc-'+top_coupon_type).removeClass('hidden');
		}
		else if (coupon_type == 'featured-coupons') {
			$('.menu-featured-coupon').hide();
			$('#mfc-'+top_coupon_type).show();
			$('#mfc-'+top_coupon_type).removeClass('hidden');
			$('#mfc-'+top_coupon_type).find('.coupon-container').show();
		}
		else if (coupon_type == 'stores') {
			$('.top-menu-store').hide();
			$('#mst-'+top_coupon_type).show();
			$('#mst-'+top_coupon_type).removeClass('hidden');
		}
	}
	$(this).parent().find('li:not(.selected)').hide();
	event.stopPropagation();
	$(this).off('click');
	$(this).closest('.expandable').on('click', expandable_select_callback);
}

function expandable_select_callback() {
	$(this).parent().parent().addClass('expanded');
	$(this).find('li:not(.selected)').show();
	$(this).off('click');
	$(this).find('.expanded-choices li').on('click', expandable_callback);
}

function merchant_button_callback() {
	var merchant_url = $(this).attr('data-href');
	track_click(merchant_url, redirect=false);
}
function track_click(url, redirect) {
	var view_url = window.location.pathname;
	var coupon_id = $.url().param('c');
	if (coupon_id) {
		view_url += '?coupon_open=' + coupon_id;
	}
	else {
		view_url += '?coupon_open=00000';
	}
	_gaq.push(['_trackPageview', view_url]);
	if (redirect) {
		window.open(url, '_blank');
	}
}

function prepend_promo_container() {
    var data = {'is_mobile': is_mobile};
	if ($('.landing-container').length == 1 && $('.promo-container').length == 0) {
		var promo_coupon = '<div class="coupon-container {{# is_mobile}}mobile-coupon-container{{/is_mobile}} promo-container" onclick="javascript:redirect_to(\'http://pushpenny.com/magazine/pushpenny-sweet-nothings-instagram-contest-2014\');"></div>';
		html = Mustache.to_html(promo_coupon, data);
		$('.coupons').prepend(html);
	}
}
