var page = 2;
$(function() {
	init_waypoint();
	$('.sorting-item a').click(function(){
		$('.sorting-item').removeClass('selected-sorting');
		$(this).parent().addClass('selected-sorting');
	});
	$('.close-tag').live('click', function() {
		$(this).parent().parent().removeClass('selected');
		$(this).parent().removeClass('selected');
		$(this).remove();
	});
	$('.filter-container').live('click', function() {
		$(this).addClass('selected')
		$(this).find('.filter-icon').addClass('selected');
		$(this).find('.filter-icon').append('<a href="javascript:void(null);" class="close-tag"><img src="images/close_tag.png"></a>');
	});
	$('.category a').live('click', function() {
		$(this).parent().removeClass('category');
		$(this).parent().addClass('current-category');
		$(this).after('<a href="javascript:void(null)" class="close-category"><img src="images/close_category.png"></a>');
	});
	$('.close-category').live('click', function() {
		$(this).parent().removeClass('current-category');
		$(this).parent().addClass('category');
		$(this).remove();
	});
	$('.coupon-container').mouseover(function() {
		if (!$(this).hasClass('coupon-banner')) {
			$(this).find('.use-coupon').show();
		}
	});
	$('.coupon-container').mouseout(function() {
		if (!$(this).hasClass('coupon-banner')) {
			$(this).find('.use-coupon').hide();
		}
	});
});
function select_categories(criteria) {
	if (criteria == 'all') {
		$('.category').each(function() {
			$(this).removeClass('category');
			$(this).addClass('current-category');
			$(this).find('a').after('<a href="#" class="close-category"><img src="images/close_category.png"></a>');
		});
	}
	else {
		$('.current-category').each(function() {
			$(this).removeClass('current-category');
			$(this).addClass('category');
			$(this).find('.close-category').remove();
		});
	}
}
function select_filters(criteria) {
	if (criteria == 'all') {
		$('.filter-container').each(function() {
			$(this).addClass('selected')
			$(this).find('.filter-icon').addClass('selected');
			$(this).find('.filter-icon').append('<a href="javascript:void(null);" class="close-tag"><img src="images/close_tag.png"></a>');
		});
	}
	else {
		$('.filter-container').each(function() {
			$(this).removeClass('selected')
			$(this).find('.filter-icon').removeClass('selected');
			$(this).find('.close-tag').remove();
		});
	}
}
function render_coupons(data) {
	var count = 0
	template = '{{#items}} \
						<div class="coupon-container {{#count}}coupon-last{{/count}}"> \
						<div class="coupon-body"> \
							<div class="coupon-header"> \
								<div class="coupon-left-label on-sale-label"> \
									<img src="/static/img/on_sale_coupon.png">On Sale \
								</div> \
								<div class="coupon-right-label"> \
									{{ merchant_name }} \
								</div> \
							</div> \
							<hr> \
							<h1 class="short-description">{{ short_desc }}</h1> \
							{{ description }}<br> \
										<span class="ends">Ends {{ end }}</span> \
										<div class="description"> \
										</div> \
									</div> \
									<div class="use-coupon"> \
										<a href="#">Use Coupon</a> \
									</div> \
									<div class="coupon-bottom"> \
										<div class="coupon-left-bottom"> \
											<a href="#"> \
												<img src="/static/img/save_coupon.png"> \
												Save \
											</a> \
										</div> \
										<div class="coupon-right-bottom"> \
											Share \
											<a href="#"><img src="/static/img/facebook_share_icon.png"></a> \
											<a href="#"><img src="/static/img/twitter_share_icon.png"></a> \
										</div> \
									</div> \
								</div> \
				{{/items}}<br clear="both">';
	data.count = function (text, render) {
    	count++;
    	if (count % 3 == 0) {
    		return true;
    	}
    	return false;
   	};
	html = Mustache.to_html(template, data);
	$('.coupons').append(html);
	
}
function init_waypoint() {
	$('.more-coupons').waypoint(function(direction) {
		if (direction === 'down') {
			var url = window.location.pathname;
			if (page > 1) {
				url += 'page/' + page + '/';
			}
			$.get(url, function(data) {
				render_coupons(data);
				if (page <= data.total_pages) {
					page += 1;
					$('.more-coupons').waypoint('destroy');
					init_waypoint();
				}
			}, 'json');
		}
	}, {
		offset: 'bottom-in-view',
	});
}
