$(function() {

  // main menu responsive
  $('.main-menu').mobileMenu({
    defaultText: 'Navigate to...',
    className: 'select-main-menu'
  });

  $('.select-main-menu').customSelect({
    customClass: 'input button dark secondary'
  });

  $('.popular-companies-list').mobileMenu({
    defaultText: 'Select company...',
    className: 'select-popular-companies-list'
  });

  // clear searchbox button functionality
  $('#clear-sb').on('click', function() {
    var field = $(this).parent().children('input');
    field.val('');
    field.focus();
  });


  // main menu indicator
  // var temp;
  // $('.main-menu li').hover(function() {
  //   temp = $(this).parent().children('.current')
  //   temp.removeClass('current');
  //   $(this).addClass('current');
  // }, function() {
  //   $(this).removeClass('current');
  //   temp.addClass('current');
  // });


  // menu-browse open/close
  var temp2 = $('.menu-browse .input');
  var temp3 = $('.main-menu .submenu-wrap');
  $('html').on('click', function() {
    temp2.children('.sub').hide();
    temp3.children('.submenu').hide();
    temp3.removeClass('opaque');
  });  
  temp2.on('click', function(event) {   
    event.stopPropagation(); 
    $(this).children('.sub').toggle();
  });
  temp3.on('click', function(event) {   
    event.stopPropagation(); 
    $(this).children('.submenu').toggle();
    if (temp3.children('.submenu').is(':visible')) {
      temp3.addClass('opaque');
    } else {
      temp3.removeClass('opaque');
    }
  });


  // main-slider
  $('.main-slider').flexslider({
    animation: "slide"
  });

  // popular companies
  $('.popular-companies').flexslider({
    animation: "slide",
    itemWidth: 134,
    itemMargin: 0,
    minItems: 2,
    maxItems: 7
  });

   // popular companies
  $('.items-carousel').flexslider({
    animation: "slide",
    itemWidth: 240,
    itemMargin: 0,
    minItems: 1,
    maxItems: 4
  });

   // testimonials
  $('.testimonials-box').flexslider({
    animation: "slide"
  });

  // checklist

  $('.checklist input').parent().removeClass('checked');
  $('.checklist input:checked').parent().addClass('checked');
  
  $('.checklist input').on('change', function() {
    if ($(this).is(':checked') && !$(this).parent().hasClass('checked')) {
      $(this).parent().addClass('checked');
    } else if (!$(this).is(':checked') && $(this).parent().hasClass('checked')) {
      $(this).parent().removeClass('checked');
    }
  });


  // days filter slider

  $( '.filter-days .slider' ).slider({
    range: true,
    min: 1,
    max: 30,
    values: [ 1, 14 ],
    slide: function( event, ui ) {
      $('.filter-days .info .begin').text( ui.values[0] + ( ui.values[0] > 1 ? ' days' : ' day' ) );
      $('.filter-days .info .end').text( ui.values[1] + ( ui.values[1] > 1 ? ' days' : ' day' ) );
    }
  });

  var begin = $('.filter-days .slider').slider('values', 0);
  var end = $('.filter-days .slider').slider('values', 1);
  $('.filter-days .info .begin').text( begin + ( begin > 1 ? ' days' : ' day' ) );
  $('.filter-days .info .end').text( end + ( end > 1 ? ' days' : ' day' ) );















});
