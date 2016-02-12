fs = require('fs');

var extractSections = function (text) {
  var lines = text.trim().split("\n"),
      start = 0,
      obj = {};

  while (start < lines.length) {
    var header = lines[start].split(/ +/);
    var key = header[1].replace(":", "");
    var length = parseInt(header[0]);
    obj[key] = lines.slice(start + 1, start + length + 1);
    start += length + 1;
  }

  return obj;
};

var parsers = {
  forts: function (string) {
    var words = string.split(/ +/);
    return {
      name:       words[0],
      x:          parseFloat(words[1]),
      y:          parseFloat(words[2]),
      owner:      words[3],
      garrison:   parseInt(words[4]),
      neighbours: []
    };
  },

  roads: function (string) {
    return string.split(/ +/);
  },

  marches: function (string) {
    var words = string.split(/ +/);
    return {
      origin:   words[0],
      target:   words[1],
      owner:    words[2],
      size:     parseInt(words[3]),
      remaining_steps: parseInt(words[4])
    };
  }
};

var parseData = function (text) {
  var sections = extractSections(text);
  var data = {};
  for (var section in parsers) {
    sections[section] = sections[section].map(function (line) {
      return parsers[section].apply(this, [line]);
    });
  }

  var forts = {};
  sections.forts.forEach(function (fort) {
    forts[fort.name] = fort;
  });

  sections.roads.forEach(function (road) {
    forts[road[0]].neighbours.push(road[1]);
    forts[road[1]].neighbours.push(road[0]);
  });

  sections.marches.forEach(function (m) {
    m.origin = forts[m.origin];
    m.target = forts[m.target];
    // TODO: update for steps
    //m.x = m.origin.x + (m.target.x - m.origin.x) * m.progress
    //m.y = m.origin.y + (m.target.y - m.origin.y) * m.progress;
    //delete m.progress;
  })

  return {
    forts:   forts,
    marches: sections.marches
  };
};

fs.readFile('sample.data', 'utf8', function (err, data) {
  if (err) { return console.log(err); }
  console.log(parseData(data));
});
