fs = require('fs');

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
  return Math.ceil(Math.pow(a.x - b.x, 2) + Math.pow(a.y - b.y, 2));
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
    fortmap[road[0]].neighbours.push(fortmap[road[1]]);
    fortmap[road[1]].neighbours.push(fortmap[road[0]]);
  });

  marches.forEach(function (m) {
    m.origin = fortmap[m.origin];
    m.target = fortmap[m.target];
    var progress = m.steps / distance(m.origin, m.target);
    m.x = progress * (m.target.x - m.origin.x) + m.origin.x;
    m.y = progress * (m.target.y - m.origin.y) + m.origin.y;

  })

  return {
    forts:   fortmap,
    marches: marches
  };
};

fs.readFile('sample.data', 'utf8', function (err, data) {
  if (err) { return console.log(err); }
  var state = parseData(data.split('\n'));
  console.log(state);
});
