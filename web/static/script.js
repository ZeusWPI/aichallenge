$(document).ready(function() {
  $(window).scroll(function() {
    if ($(window).scrollTop() >= window.innerHeight / 3) {
      $('#container').addClass('fixed-header');
    } else {
      $('#container').removeClass('fixed-header');
    }
  });
});
