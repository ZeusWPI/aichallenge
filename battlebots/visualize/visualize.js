FORT_RADIUS = 1;
NEUTRAL_NAME = "neutral";
NEUTRAL_COLOR = "#7f7f7f";
PLAYER_COLORS = [
  "#1f77b4",
  "#ff7f0e",
  "#2ca02c",
  "#d62728",
  "#9467bd",
  "#8c564b",
  "#e377c2",
  "#bcbd22",
  "#17becf"
];
VISUALIZER = new MosiacVisualizer();

/**
* Remove header from section and collect lines in an array
* @param {array} lines unparsed lines, array will be modified
* @return {array} array of lines in the section defined by the header
*/
var takeSection = function (lines) {
  var header = lines.shift().split(/ +/);
  var length = parseInt(header[0]);
  var section = [];
  for (var i = 0; i < length; i++) {
    section.push(lines.shift());
  }
  return section;
};

/**
* Remove header from section and collect lines in an array
* @param {string} string unparsed line that defines a fort
* @return {object} returns a fort object with no neighbours
*/
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

/**
* Parses road by splitting into words
* @param {string} string unparsed line that defines a road
* @return {array} returns array of strings containing words
*/
var parseRoad = function (string) {
  return string.split(/ +/);
};


/**
* Parses road by splitting into words
* @param {string} string unparsed line that defines a march
* @return {object} returns a march object
*/
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

var parseData = function (lines, turn) {
  // Take fort section and parse each line with respective parse function
  var forts = takeSection(lines).map(parseFort);
  var roads = takeSection(lines).map(parseRoad);
  var marches = takeSection(lines).map(parseMarch);

  // Maps fortname on respective fort
  var fortmap = {};
  forts.forEach(function (fort) {
    fortmap[fort.name] = fort;
  });

  // Replaces road name with actual road in road object
  roads.forEach(function (road) {
    road[0] = fortmap[road[0]];
    road[1] = fortmap[road[1]];
  });
  var game = {
    // save forts as d3 associative array
    forts:   forts,
    roads:   roads,
    marches: marches
  };
  VISUALIZER.setup(game);

  return game;
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

var visualize = function(game){
  $('#control-slider').on('change', function(e) {
    VISUALIZER.draw(game, parseInt(e.target.value));
  });
  $('#control-slider').attr('min', 0);
  $('#control-slider').attr('max', game.steps.length-1);
  VISUALIZER.draw(game, 0);
};

Game = function(steps) {
  this.steps = steps;
  this.playerColors = {};
  this.playerColors[NEUTRAL_NAME] = NEUTRAL_COLOR;
};

Game.prototype.getPlayerColor = function(name){
  var color = this.playerColors[name];
  if (color === undefined) {
    var num = Object.keys(this.playerColors).length - 1;
    this.playerColors[name] = PLAYER_COLORS[num];
    color = PLAYER_COLORS[num];
  }
  return color;
};


var visualizeLog = function(log){
  var raw = log.split('\n');
  lines = [];
  raw.forEach(function(val){
    // If line is not a comment or an invalid operation add to lines
    if(! /^(#.*)?$/.test(val)){
      lines.push(val);
    }
  });

  var steps = [];
  // Shift line frome lines and parse until all lines are parsed
  while (lines.length > 0) {
    steps.push(parseData(lines, steps.length));
  }
  visualize(new Game(steps));
};

$(document).ready(function(){
  var reader = new FileReader();
  reader.onload = function(e){
    visualizeLog(e.target.result);
  };
  reader.onerror = function(e){
    alert("could not open file");
  };
  // When file is chosen
  $("#file-chooser").change(function(e){
    // Read file "e.target.files[0]" as text
    reader.readAsText(e.target.files[0]);
  });
});
