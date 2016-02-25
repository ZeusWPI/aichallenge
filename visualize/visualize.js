var FORT_RADIUS = 1;
var CURRENT_STEP = 0;

var takeSection = function (lines) {
  var header = lines.shift().split(/ +/);
  var length = parseInt(header[0]);
  var section = [];
  for (var i = 0; i < length; i++) {
    section.push(lines.shift());
  }
  return section;
};

var parseFort = function (string) {
  var words = string.split(/ +/);
  return {
    name:       words[0],
    x:          parseInt(words[1]),
    y:          parseInt(words[2]),
    owner:      words[3],
    garrison:   parseInt(words[4]),
    neighbours: []
  };
};

var parseRoad = function (string) {
  return string.split(/ +/);
};

var parseMarch = function (string) {
  var words = string.split(/ +/);
  return {
    origin: words[0],
    target: words[1],
    owner:  words[2],
    size:   parseInt(words[3]),
    steps:  parseInt(words[4])
  };
};

var parseData = function (lines) {
  var forts = takeSection(lines).map(parseFort);
  var roads = takeSection(lines).map(parseRoad);
  var marches = takeSection(lines).map(parseMarch);

  var fortmap = {};
  forts.forEach(function (fort) {
    fortmap[fort.name] = fort;
  });

  roads.forEach(function (road) {
    road[0] = fortmap[road[0]];
    road[1] = fortmap[road[1]];
  });

  marches.forEach(function (m) {
    m.origin = fortmap[m.origin];
    m.target = fortmap[m.target];
    var dx = m.target.x - m.origin.x;
    var dy = m.target.y - m.origin.y;
    var alpha = Math.atan2(dy, dx);
    var x_step = Math.cos(alpha);
    var y_step = Math.sin(alpha);
    var dist = Math.ceil(dx / x_step);

    var dx_gates = dx - 2 * FORT_RADIUS * x_step;

    var k = (dx_gates/(dist-1)) / x_step;
    m.x = m.target.x - x_step * (FORT_RADIUS + k * (m.steps-0.5));
    m.y = m.target.y - y_step * (FORT_RADIUS + k * (m.steps-0.5));
    m.step_size = k;
  });

  return {
    forts:   d3.values(fortmap),
    roads:   roads,
    marches: marches
  };
};

var viewbox = function(xmin, ymin, xmax, ymax, edge){
  edge = edge || 0;
  return [xmin-edge, ymin-edge, xmax+2*edge, ymax+2*edge].map(function(n){
    return n.toString();
  }).join(' ');
};

var translate = function(x, y){
  return "translate("+x+","+y+")";
};

var visualize = function(steps){
  var drawstep = function(i) {
    draw(steps[i]);
    d3.select("#next-step").on("click", function(){ drawstep(i+1); });
  };
  drawstep(0);
};

var draw = function(data){
  var xmax = d3.max(data.forts, function(f) { return f.x });
  var ymax = d3.max(data.forts, function(f) { return f.y });

  var players = d3.set(
    data.forts.map(function(f) {return f.owner}),
    function(f) {return f}
  ).values();

  var playercolor = d3.scale.category10().domain(players);

  var fig = d3.select("#visualisation")
      .attr("viewBox", viewbox(0, 0, xmax, ymax, 2))
      .attr("width", "100%");

  fig.selectAll("line")
      .data(data.roads)
      .enter().append("line")
      .attr("stroke-width", 0.1)
      .attr("stroke", "gray")
      .attr("x1", function(d) {return d[0].x})
      .attr("y1", function(d) {return d[0].y})
      .attr("x2", function(d) {return d[1].x})
      .attr("y2", function(d) {return d[1].y});


  var marches = fig.selectAll(".march")
      .data(data.marches)
      .enter().append("g")
      .attr("class", "march");

  marches.append("circle")
      .attr("r", function(d) {return d.step_size/2})
      .attr("fill", function(d) {return playercolor(d.owner)});

  marches.append("text")
      .text(function(d) {return d.size})
      .attr("font-size", function(d) {return .8*d.step_size})
      .attr("fill", "#fff")
      .attr("dy","0.3em")
      .attr("text-anchor", "middle");

  fig.selectAll(".march")
      .data(data.marches)
      .attr("transform", function(d) {return translate(d.x, d.y)});

  var fortGroups = fig.selectAll(".fort")
      .data(data.forts)
      .enter().append("g")
      .attr("class", "fort")
      .attr("transform", function(d) {return translate(d.x, d.y)});

  fortGroups.append("circle")
      .attr("r", FORT_RADIUS)
      .attr("fill", function(d) {return playercolor(d.owner)});

  fortGroups.append("text")
      .text(function(d) {return d.garrison})
      .attr("font-size", .9 * FORT_RADIUS)
      .attr("fill", "#fff")
      .attr("dy","0.3em")
      .attr("text-anchor", "middle");
};


$.get('../sample.data', function(dump){
  var raw = dump.split('\n'), lines = [];
  raw.forEach(function(val){
    if(! /^(#.*)?$/.test(val)){
      lines.push(val);
    }
  });
  var steps = [];
  while (lines.length > 0) {
    steps.push(parseData(lines));
  }
  visualize(steps);
});
