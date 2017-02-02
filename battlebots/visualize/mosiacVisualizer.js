var MosiacVisualizer = function() {
    var getAngle = function(p1, p2) {
        var dx = p2[0] - p1[0];
        var dy = p2[1] - p1[1];
        return Math.atan2(dy, dx);
    };

    var getNormal = function(p1, p2) {
        // D3 uses counter clockwise polygons so 90 degree offset
        return getAngle(p1, p2) - Math.PI / 2;
    };

    var findMiddle = function(edge) {
        var dx = edge[1][0] - edge[0][0];
        var dy = edge[1][1] - edge[0][1];
        return [edge[0][0] + dx / 2, edge[0][1] + dy / 2];
    }

    this.setup = function(game) {
        var roads = game.roads;
        var forts = game.forts;
        game.path = [];
        roads.forEach(function(road) {
            road[0].neighbours.push(road[1]);
            road[1].neighbours.push(road[0]);
        });
        var size = FORT_RADIUS*1.2;
        forts.forEach(function(fort) {
            var maxOff = size * 0.5;
            var nrPoints = fort.neighbours.length;
            if (nrPoints < 3) nrPoints += 3 - nrPoints;
            fort.points = [];
            for (var i = 0; i < nrPoints; i++) {
                var offset = Math.random() * maxOff - maxOff;
                var angleOffset = Math.random() * Math.PI / 2;
                var theta = angleOffset + (i / nrPoints) * (Math.PI * 2);
                var x = Math.cos(theta) * (size + offset);
                var y = Math.sin(theta) * (size + offset);
                fort.points.push([x, y]);
            }

            fort.freeEdges = fort.neighbours.slice().map(function(n) {
                return true;
            });
        });

        var distSq = function(point1, point2) {
            return Math.pow(point1[0] - point2[0], 2) + Math.pow(point1[1] - point2[1], 2);
        };
        var maxRec = 1000;
        var currRec = 0;
        var connectEdges = function(startEdge, targetEdge, path) {
            if (currRec > maxRec) return;
            currRec++;
            var targetPoint = targetEdge[0];
            var distance = distSq(startEdge[0], targetPoint);
            var smallestDist = distSq(startEdge[1], targetPoint);
            if (smallestDist > distance) smallestDist = distance;
            // We are close enough to other edge to connect with one polygon
            if (parseFloat(smallestDist).toFixed() <= 2) {
                //TODO Fix stitching errors
                var x1 = targetEdge[0];
                var x2 = startEdge[0];
                var y1 = targetEdge[1];
                var y2 = startEdge[1];
                path.push([x1, x2, y2, y1]);
            } else {
                // Else calculate next step
                // Calculate the edge's normal
                var normal = getNormal(startEdge[0], startEdge[1]);
                var sizeX = startEdge[1][0] - startEdge[0][0];
                var sizeY = startEdge[1][1] - startEdge[0][1];

                // Calculate our target direction
                var targetDir = getAngle(startEdge[0], targetPoint);
                //console.log(targetDir * (180 / Math.PI));
                var diff = (targetDir - normal);
                diff = (diff + Math.PI) % (Math.PI * 2) - Math.PI;
                // Calculate the direction our new extrution will follow
                var theta = Math.min(Math.max(diff, -Math.PI / 4.5), Math.PI / 4.5);
                var dir = normal + theta;

                // Generate edge in direction
                var normalPoint1 = [startEdge[0][0] + Math.cos(dir), startEdge[0][1] + Math.sin(dir)];
                var normalPoint2 = [normalPoint1[0] + Math.cos(dir + Math.PI / 2), normalPoint1[1] + Math.sin(dir + Math.PI / 2)];

                connectEdges(startEdge, [normalPoint1, normalPoint2], path);
                connectEdges([normalPoint1, normalPoint2], targetEdge, path);
            }

        };

        var getNextFreeEdge = function(fort) {
            var edge = 0;
            while (!fort.freeEdges[edge]) {
                edge++;
                if (edge > fort.freeEdges.length) {
                    return -1;
                }
            }
            fort.freeEdges[edge] = false;
            var point2 = fort.points[0];
            if (edge + 1 != fort.points.length) {
                var point2 = fort.points[edge + 1];
            }
            return [fort.points[edge].slice(), point2.slice()];
        }
        var getBestFreeEdge = function(fort, other) {
            // TODO
        }
        var road = roads[0];
        roads.forEach(function(road) {
            var originFort = road[0];
            var targetFort = road[1];

            var startEdge = getNextFreeEdge(originFort, targetFort);
            var targetEdge = getNextFreeEdge(targetFort, originFort);
            // Convert target edge in global coordinates
            targetEdge.forEach(function(edge) {
                edge[0] += targetFort.x;
                edge[1] += targetFort.y;
            });
            startEdge.forEach(function(edge) {
                edge[0] += originFort.x;
                edge[1] += originFort.y;
            });

            // Calc middle edge
            var middleDir = getAngle(startEdge[0], targetEdge[0]) - Math.PI/2;
            var p1 = findMiddle([startEdge[0], targetEdge[0]]);
            var middleEdge = [p1, [p1[0] + Math.cos(middleDir), p1[1] + Math.sin(middleDir)]];

            var path = [];
            connectEdges(startEdge, [middleEdge[1], middleEdge[0]], path);
            connectEdges(targetEdge, middleEdge, path);
            path.forEach(function(polygon) {
                game.path.push({
                    edges: polygon,
                    x: 0,
                    y: 0
                });
            });
        });
    }

    this.draw = function(game, step) {
        var data = game.steps[step];
        // Find min max for all displayed forts
        var xmin = d3.min(data.forts, function(f) {
            return f.x
        });
        var ymin = d3.min(data.forts, function(f) {
            return f.y
        });
        var xmax = d3.max(data.forts, function(f) {
            return f.x
        });
        var ymax = d3.max(data.forts, function(f) {
            return f.y
        });

        var speed = parseInt($("#speed-slider").val());

        var fig = d3.select("#graph");

        // Set our viewbox and define transitions
        fig.transition()
            .duration(speed)
            .attr("viewBox", viewbox(xmin, ymin, xmax - xmin, ymax - ymin, 2));

        // FORTS

        var forts = fig.select("#forts").selectAll(".fort")
            .data(data.forts);

        var newForts = forts.enter().append("g")
            .attr("class", "fort")
            .attr("transform", function(d) {
                return translate(d.x, d.y)
            });

        newForts.append("polygon")
            .attr("points", function(d) {
                return d.points.slice().map(function(p) {
                    return p.join(",")
                }).join(" ");
            })
            .attr("fill", function(d) {
                return game.getPlayerColor(d.owner)
            });

        newForts.append("text")
            .attr("font-size", .9 * FORT_RADIUS)
            .attr("fill", "#fff")
            .attr("dy", "0.3em")
            .attr("text-anchor", "middle");

        forts.select("polygon")
            .transition()
            .duration(speed)
            .attr("fill", function(d) {
                return game.getPlayerColor(d.owner)
            });

        forts.select("text")
            .text(function(d) {
                if (d.garrison != 0) return d.garrison
            });

        forts.exit().remove();

        forts.attr("transform", function(d) {
            return translate(d.x, d.y)
        });

        // ROADS

        var roads = fig.select("#roads").selectAll(".path")
            .data(data.path, function(d) {
                return d.edges[0] + " " + d.edges[1];
            });
        var newRoads = roads.enter().append("g")
            .attr("class", "path")
            .attr("transform", function(d) {
                return translate(d.x, d.y)
            });
        newRoads.append("polygon")
            .attr("points", function(d) {
                return d.edges.slice().map(function(p) {
                    return p.join(",")
                }).join(" ");
            })
            .attr("stroke-width", 0.05)
            .attr("stroke", "black")
            .attr("fill", "green");

        roads.exit().remove();
        roads.attr("transform", function(d) {
            return translate(d.x, d.y)
        });
    }
}
