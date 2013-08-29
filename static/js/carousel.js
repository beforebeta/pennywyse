$(function(){
  $('#carousel .carousel ul').on('click', 'li', function(){
    var db = $(this).data();
    $(this).closest('ul').find('img').removeClass('active');
    $(this).children('img:first').addClass('active');
    $('#carousel .selected img').attr('src', db.image);
    $('#carousel .selected h1').text(db.shortdesc + ' at ' + db.merchantname);
    $('#carousel .selected .description').text(db.description);
    $('#carousel .selected .button').attr('href', db.couponurl);
    $('#carousel .selected .merchantlink').attr('href', db.merchanturl);
    $('#carousel .selected .merchantlink').text(db.merchantname);
  });

  $('#carousel').jCarouselLite({
    autoCSS: true,
    autoWidth: true,
    visible: 7,
    responsive: true,
    btnNext: '.next',
    btnPrev: '.prev',
    scroll: 5
  });
});
