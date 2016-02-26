$(document).ready(function() {
  var slider = $('#control-slider');
  var playing = false;

  var update_turn = function( new_turn ) {
    $(slider).val(new_turn);
    $(slider).change();
  }

  var update_inputs = function() {
    var new_val = $(slider).val();

    $('#control-label').val(new_val);
    $('[data-step]').prop('disabled', function() {
      step_val = parseInt(new_val) + parseInt($(this).data('step'));
      return step_val < parseInt($(slider).attr('min')) || step_val > parseInt($(slider).attr('max'));
    });
  }

  $(slider).bind('input', update_inputs);
  $(slider).bind('change', update_inputs);

  $('[data-step]').on('click', function() {
    var step = parseInt($(this).data('step'));
    var new_val = parseInt($(slider).val()) + step;
    update_turn(new_val);
  });

  var updatePlaying = function( newState ) {
    playing = newState;
    $('#play').text(playing ? "Pause" : "Play");
  }

  var startPlaying = function() {
    slider_val = parseInt($(slider).val());
    if (playing) {
      update_turn(++slider_val);
      setTimeout(startPlaying, parseInt($("#speed-slider").val()));
      if (slider_val >= parseInt($("#control-slider").attr('max'))) { updatePlaying(false); }
    }
  }
  $('#play').on('click', function() { updatePlaying(!playing); startPlaying(); });

  update_turn(0);
});
