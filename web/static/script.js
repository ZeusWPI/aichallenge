$(document).ready(function() {
   //cache selectors
  var headers = $('.content h1');
  var navbar_items = $('nav > .toc > ul > li');

  $(window).scroll(function(){
    if ($(window).scrollTop() >= window.innerHeight/3) {
      $('#container').addClass('fixed-header');
    } else {
      $('#container').removeClass('fixed-header');
    }
    navbar_items.removeClass('focused');
    var focused_id = headers.filter(function() {
      return $(window).scrollTop() >= $(this).offset().top -1;
    }).last().attr('id');
    $('nav a[href="#'+ focused_id +'"]').parent().addClass('focused');
  });
});
