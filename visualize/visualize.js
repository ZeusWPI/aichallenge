var FORT_RADIUS = 1;

var takeSection = function (lines) {
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

var distance = function(a, b) {
  return Math.ceil(
    Math.sqrt(Math.pow(a.x - b.x, 2) + Math.pow(a.y - b.y, 2))
  );
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
    var dist = distance(m.origin, m.target);
    var xspeed = (m.target.x - m.origin.x - 2*FORT_RADIUS)/dist;
    var yspeed = (m.target.y - m.origin.y - 2*FORT_RADIUS)/dist;
    m.x = m.target.x - FORT_RADIUS - xspeed * m.steps;
    m.y = m.target.y - FORT_RADIUS - yspeed * m.steps;
  });

  return {
    forts:   d3.values(fortmap),
    roads:   roads,
    marches: marches
  };
};

var viewbox = function(xmin, ymin, xmax, ymax, edge){
  edge = edge || 0;
  return [xmin-edge, ymin-edge, xmax+edge, ymax+edge].map(function(n){
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
      .attr("viewBox", viewbox(0, 0, xmax, ymax, 2));

  fig.selectAll("line")
      .data(data.roads)
      .enter().append("line")
      .attr("stroke-width", 0.1)
      .attr("stroke", "gray")
      .attr("x1", function(d) {return d[0].x})
      .attr("y1", function(d) {return d[0].y})
      .attr("x2", function(d) {return d[1].x})
      .attr("y2", function(d) {return d[1].y});

  console.log(data.marches);

  fig.selectAll("circle")
      .data(data.marches)
      .enter().append("circle")
      .attr("r", 0.5)
      .attr("cx", function(d) {return d.x})
      .attr("cy", function(d) {return d.y})
      .attr("fill", function(d) {return playercolor(d.owner)});

  var fortGroups = fig.selectAll("g")
      .data(data.forts)
      .enter().append("g")
      .attr("transform", function(d) {return translate(d.x, d.y)});

  fortGroups.append("circle")
      .attr("r", FORT_RADIUS)
      .attr("fill", function(d) {return playercolor(d.owner)});

  fortGroups.append("text")
      .text(function(d) {return d.garrison})
      .attr("font-size", ".8px")
      .attr("fill", "#fff")
      .attr("text-anchor", "middle")
      .attr("dy", ".3em");
}


$.get('../map.data', function(dump){
  var data = parseData(dump.split('\n'));
  draw(data);
});
