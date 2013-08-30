$(function(){
  $('#carousel .carousel ul li .coupon').on('click', function(){
    var db = $(this).closest('li').data();
    $(this).closest('ul').find('li .coupon.active').removeClass('active');
    $('.coupon-' + db.couponid).addClass('active');
    $('#carousel .selected img').attr('src', db.image);
    $('#carousel .selected h1').text(db.shortdesc + ' at ' + db.merchantname);
    $('#carousel .selected .description').text(db.description);
    $('#carousel .selected .button').attr('href', db.couponurl);
    $('#carousel .selected .merchantlink').attr('href', db.merchanturl);
    $('#carousel .selected .merchantlink').text(db.merchantname);
  });

  $('#carousel .carousel-row').jCarouselLite({
    autoCSS: true,
    autoWidth: true,
    visible: 6,
    responsive: true,
    btnNext: '.next',
    btnPrev: '.prev',
    scroll: 5
  });
});
