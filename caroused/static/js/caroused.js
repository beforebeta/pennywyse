$(function(){
	$('#caroused .carousel ul').on('click', 'li', function(){
		var db = $(this).data();
		$(this).closest('ul').find('img').removeClass('active');
		$(this).children('img:first').addClass('active');
		$('#caroused .selected img').attr('src', db.image);
		$('#caroused .selected h2').text(db.shortdesc + ' at ' + db.merchantname);
		$('#caroused .selected .description').text(db.description);
		$('#caroused .selected .button').attr('href', db.couponurl);
		$('#caroused .selected .merchantlink').attr('href', db.merchanturl);
		$('#caroused .selected .merchantlink').text(db.merchantname);
	});

	$('#caroused').jCarouselLite({
		autoCSS: true,
		autoWidth: true,
		visible: 8,
		responsive: true,
		btnNext: '.next',
		btnPrev: '.prev',
		scroll: 8
	});
});
