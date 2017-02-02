$(document).ready(function() {
  var slider = $('#control-slider');
  var playpause = $('#playpause');

  var update_turn = function( new_turn ) {
    slider.val(new_turn);
    slider.change();
  };

  $('[data-step]').on('click', function() {
    var step = parseInt($(this).data('step'));
    var new_val = parseInt(slider.val()) + step;
    update_turn(new_val);
  });

  $.each($('[data-bind]'), function() {
    var binded = $(this);
    var binder = $($(this).data('bind'));
    binder.bind('input change', function() {
      binded.val($(this).val());
      binded.text($(this).val());
    });
    binder.change(); // Initialize the label
  });

  var togglePlaying = function() {
    if (playpause.hasClass('active')) {
      sliderVal      = parseInt(slider.val());
      animationSpeed = parseInt($("#speed-slider").val());
      sliderMax      = parseInt($("#control-slider").attr('max'));

      update_turn(++sliderVal);
      setTimeout(togglePlaying, animationSpeed);
      if (sliderVal >= sliderMax) { playpause.removeClass('active'); }
    }
  };

  playpause.on('click', function() {
    playpause.toggleClass('active');
    togglePlaying();
  });

  d3.select('#opts')
  .on('change', function() {
    var vis = eval(d3.select(this).property('value'));
    VISUALIZER = vis;
  });

  update_turn(0);
});
