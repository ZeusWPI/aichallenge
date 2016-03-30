$(document).ready(function() {
  $(window).scroll(function() {
    if ($(window).scrollTop() >= window.innerHeight / 3) {
      $('.navbar').addClass('navbar-fixed-top');
      $('#below-navbar').addClass('fixed-header');
    } else {
      $('.navbar').removeClass('navbar-fixed-top');
      $('#below-navbar').removeClass('fixed-header');
    }
  });
});
