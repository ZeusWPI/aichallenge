var FORT_RADIUS = 1;

var takeSection = function (lines) {
  console.log("taking section from length" + lines.length);
  var header = lines.shift().split(/ +/);
  var length = parseInt(header[0]);
  var section = []
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
}

var translate = function(x, y){
  return "translate("+x+","+y+")";
}

var draw = function(data){
  var xmax = d3.max(data.forts, function(f) { return f.x });
  var ymax = d3.max(data.forts, function(f) { return f.y });

  var players = d3.set(
    data.forts.map(function(f) {return f.owner}),
    function(f) {return f}
  ).values();



  var playercolor = d3.scale.category10().domain(players);

  var fig = d3.select("#visualisation")
      .append("svg")
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


  var marchGroups = fig.selectAll(".march")
      .data(data.marches)
      .enter().append("g")
      .attr("class", "march")
      .attr("transform", function(d) {return translate(d.x, d.y)});

  marchGroups.append("circle")
      .attr("r", function(d) {return d.step_size/2})
      .attr("fill", function(d) {return playercolor(d.owner)});

  marchGroups.append("text")
      .text(function(d) {return d.size})
      .attr("font-size", function(d) {return .8*d.step_size})
      .attr("fill", "#fff")
      .attr("text-anchor", "middle");


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
      .attr("text-anchor", "middle");
}


$.get('../map.data', function(dump){
  var lines = dump.split('\n');
  lines.pop(); // remove final empty line
  var steps = [];
  while (lines.length > 0) {
    steps.push(parseData(lines));
  }
  draw(steps[1]);
});
