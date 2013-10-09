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
      try{
          $("#filter_form").submit();
      }catch(e){}
  });

  $("#clear_categories").click(function(e){
      e.preventDefault();
      try{
          $('.checklist input').prop('checked', false);
          try{
              $("#filter_form").submit();
          }catch(e){}
      }catch(e){console.log(e);}
      return false;
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


    //setup support for csrf
    $(document).ajaxSend(function(event, xhr, settings) {
        function getCookie(name) {
            var cookieValue = null;
            if (document.cookie && document.cookie != '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) == (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
        function sameOrigin(url) {
            // url could be relative or scheme relative or absolute
            var host = document.location.host; // host + port
            var protocol = document.location.protocol;
            var sr_origin = '//' + host;
            var origin = protocol + sr_origin;
            // Allow absolute or scheme relative URLs to same origin
            return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
                (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
                // or any other URL that isn't scheme relative or absolute i.e relative.
                !(/^(\/\/|http:|https:).*/.test(url));
        }
        function safeMethod(method) {
            return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
        }

        if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    });

    $('body').on('click', '#subscribe_button', function(e){
        var $this = $(this);
//        var full_name = $('#subscribe_full_name').val();
        var email = $('#subscribe_email').val();
        var $subscribe_bar = $("#subscribe_bar");
        var $row = $("#subscribe_bar_row");
        e.preventDefault();
        try{
//            if(full_name.length<2){
//                alert("Please enter your name");
//                return false;
//            } else {
                if( (email.length<2) ||  (email.indexOf("@")<0) || (email.indexOf(".")<0)) {
                    alert("Please enter a valid email address");
                } else {
                    $.ajax({
                        type: "POST",
                        data: {'full_name':email, 'email':email},
                        url: '/a/subscribe/',
                        cache: false,
                        dataType: "json",
                        success: function(response, textStatus) {
                            if(response["status"] == "0") {
                                alert(response["text"]);
                            } else {
                                $this.val("Thank You");
                                $this.removeClass("blue");
                                $this.addClass("dark");
                                $this.attr("disabled","disabled");
                                try{
                                    mixpanel.track("Email Subscribe");
                                }catch(e){}
                            }
                            try{
                                _gaq.push(['_trackEvent', 'contact', 'email subscription', 'homepage',, false]);
                            } catch(e){
                                try {
                                    console.log(e);
                                } catch(e){}
                            }
                        },
                        error: function (XMLHttpRequest, textStatus, errorThrown) {
                            try{
                                console.log(textStatus);
                                console.log(errorThrown);
                            } catch(e){}
                        }
                    });
                }
//            };
        } catch(e){}
        return false;
    });

    // Click Tracking
    $("a[rel=comm]").click(function(e){
        var url = this.href;
        try{
            $.ajax({
                async: false,
                type: "POST",
                url: "/a/clk/",
                data: {
                    clicked: url
                },
                contentType: "application/x-www-form-urlencoded; charset=UTF-8",
                cache: false
            });
        }catch(e){}
        return true;
    });
    
    $('#categories_filter').change(function(){
  		$('form[name=categories_filter]').submit();

    })
    $('.side-pagination').change(function(){
    	var page = $('.side-pagination').find('option:selected').val();
    	var category = $('#categories_filter').find('option:selected').val()
    	var redirection_url = '';
    	if (page != '...') {
    		redirection_url = '/stores/' + page + '/';
    	}
    	if (category) {
    		redirection_url += '?category=' + category;
    	}
    	location.href = redirection_url;
    });
});
