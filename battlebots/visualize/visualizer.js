var Visualizer = function(){
  this.setup = function(game){
    game.marches.forEach(function (m) {
      // Replace fortnames with actual fort objects
      m.origin = fortmap[m.origin];
      m.target = fortmap[m.target];
      // Calculate distance between forts
      var dx = m.target.x - m.origin.x;
      var dy = m.target.y - m.origin.y;

      // Calculate angle between forts
      var alpha = Math.atan2(dy, dx);
      // Define step movement as the legs of right triagle
      var x_step = Math.cos(alpha);
      var y_step = Math.sin(alpha);

      // Calculate eucledean distance
      var dist = Math.sqrt(Math.pow(dx, 2) + Math.pow(dy, 2));
      // Create steps in function of eucledean distance rounded up
      var steps = Math.ceil(dist);

      // Calculate movement per step using acual fort distance accounting for
      // fort xy being its center point
      // (actual road length) / steps
      var k = (dist - 2 * FORT_RADIUS) / (steps - 1);

      // Cacluate current march postition
      // target x - (x speed from angle * (we don't want to be in forts so substract fort raduis + (actual step size * current martch steps taken)))
      m.x = m.target.x - x_step * (FORT_RADIUS + k * (m.steps-0.5));
      m.y = m.target.y - y_step * (FORT_RADIUS + k * (m.steps-0.5));
      m.step_size = k;

      m.id = [m.origin.name, m.target.name, turn + m.steps - dist].join(' ');
    });
  }

  this.drawLegend = function(game){
    var entryHeight = 20;
    var fig = d3.select("#legend");
    var newEntries = fig.selectAll(".legend-entry")
        .data(Object.keys(game.playerColors, function(d){return d}))
        .enter().append('g')
        .attr('class', 'legend-entry')
        .attr('transform', function(d, i){
          return translate(0, i * entryHeight);
        });

    newEntries.append('circle')
        .attr('cy', 8)
        .attr('cx', 8)
        .attr('r', 8)
        .attr('fill', function(d) {return game.getPlayerColor(d)});

    newEntries.append('text')
        .attr('x', 20)
        .attr('y', 12)
        .text(function(d) {return d});
  };

  this.draw = function(game, step){
    var data = game.steps[step];
    // Find min max for all displayed forts
    var xmin = d3.min(data.forts, function(f) { return f.x });
    var ymin = d3.min(data.forts, function(f) { return f.y });
    var xmax = d3.max(data.forts, function(f) { return f.x });
    var ymax = d3.max(data.forts, function(f) { return f.y });

    var speed = parseInt($("#speed-slider").val());

    var fig = d3.select("#graph");

    // Set our viewbox and define transitions
    fig.transition()
        .duration(speed)
        .attr("viewBox", viewbox(xmin, ymin, xmax-xmin, ymax-ymin, 2));

    // ROADS

    var roads = fig.select("#roads").selectAll("line")
        .data(data.roads, function(d) {return d[0].name + " " + d[1].name});

    roads.enter().append("line")
        .attr("stroke-width", 0.1)
        .attr("stroke", "gray")
        .attr("x1", function(d) {return d[0].x})
        .attr("y1", function(d) {return d[0].y})
        .attr("x2", function(d) {return d[1].x})
        .attr("y2", function(d) {return d[1].y});

    roads.exit().remove();

    // MARCHES

    var marches = fig.select("#marches").selectAll(".march")
        .data(data.marches, function(d) {return d.id});

    var newMarches = marches.enter().append("g")
      .attr("class", "march");

    // animate new marches
    newMarches.style("opacity", 0)
      .attr("transform", function(d) {return translate(d.origin.x, d.origin.y)})
      .transition()
      .duration(speed)
      .style("opacity", 1)
      .attr("transform", function(d) {return translate(d.x, d.y)});



    newMarches.append("circle")
        .attr("r", function(d) {return d.step_size*0.5})
        .attr("fill", function(d) {return game.getPlayerColor(d.owner)});

    newMarches.append("text")
        .attr("font-size", function(d) {return .8*d.step_size})
        .attr("fill", "#fff")
        .attr("dy", function(d) {return .3*d.step_size})
        .attr("text-anchor", "middle")
        .text(function(d) {return d.size});

    marches.select("text")
        .text(function(d) {return d.size});

    marches.data(data.marches, function(d) {return d.id})
        .transition()
        .duration(speed)
        .attr("transform", function(d) {return translate(d.x, d.y)})
        .style("opacity", 1);

    marches.exit()
        .transition()
        .duration(speed)
        .attr("transform", function(d) {
          // arriving marches
          if (d.steps == 1) {
            return translate(d.target.x, d.target.y)
          }
          return translate(d.x, d.y);
        })
        .style("opacity", 0)
        .remove();


    // FORTS

    var forts = fig.select("#forts").selectAll(".fort")
        .data(data.forts);

    var newForts = forts.enter().append("g")
        .attr("class", "fort")
        .attr("transform", function(d) {return translate(d.x, d.y)});

    newForts.append("circle")
        .attr("r", FORT_RADIUS)
        .attr("fill", function(d) {return game.getPlayerColor(d.owner)});

    newForts.append("text")
        .attr("font-size", .9 * FORT_RADIUS)
        .attr("fill", "#fff")
        .attr("dy","0.3em")
        .attr("text-anchor", "middle");

    forts.select("circle")
        .transition()
        .duration(speed)
        .attr("fill", function(d) {return game.getPlayerColor(d.owner)});

    forts.select("text")
        .text(function(d) {return d.garrison});

    forts.exit().remove();

    forts.attr("transform", function(d) {return translate(d.x, d.y)});

    this.drawLegend(game);
  }
}
