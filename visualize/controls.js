$(document).ready(function() {
  var slider = $('#control-slider');

  var update_turn = function( new_turn ) {
    $(slider).val(new_turn);
    $(slider).change();
  }

  var update_inputs = function() {
    var new_val = $(slider).val();

    $('#control-label').val(new_val);
  }

  $(slider).bind('input', update_inputs);
  $(slider).bind('change', update_inputs);

  $('[data-step]').on('click', function() {
    var step = parseInt($(this).data('step'));
    var new_val = parseInt($(slider).val()) + step;
    update_turn(new_val);
  });

  update_turn(0);
});
