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
      name:     words[0],
      x:        parseFloat(words[1]),
      y:        parseFloat(words[2]),
      owner:    words[3],
      garrison: parseInt(words[4])
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
      position: parseFloat(words[4])
    };
  }
};

var parseData = function (text) {
  var sections = extractSections(text);
  var data = {};
  for (var section in parsers) {
    data[section] = sections[section].map(function (line) {
      console.log(line);
      return parsers[section].apply(this, [line]);
    });
  }
  return data;
};

fs.readFile('sample.data', 'utf8', function (err, data) {
  if (err) { return console.log(err); }
  console.log(parseData(data));
});
