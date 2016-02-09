
## Description of internal state

The internal state consists of players (and their bots processes) and the
playing field.

A player has a unique name.

A playing field consists of a graph. For each node in the graph, the position
in an orthogonal coordinate system, the amount of armies and their alliances,
and the neighbouring nodes are stored. For each edge in the graph, any
wandering armies and their positions are stored.

## Interface to Bots

At the start of the game, the bot is told about the amount of armies in his
home base, located at (from viewpoint of the bot) the origin of the coordinate
system.

Upon occupying a new node (including the home base at the start of the game),
the bot is told about all edges adjacent to the new node. This of course
includes the position of the node "at the other end" of these edges.

At the beginning of each iteration, the bot is told about the locations of all
armies in his line of sight. The line of sight of a bot consists of:
- All nodes currently occupied by the bot;
- All neighbouring nodes of the nodes currently occupied by the bot;
- All edges interconnecting above nodes.

In case of an army located in a node, the bot is told about the size of this
army. For an army located on an edge, the bot is told about the direction and
the position (as a ratio of the edge) of the army.

## Protocol
For clarity: comments and ellipses are not part of the protocol :-)

    20 forts:
    # fort xcoord ycoord owner armysize
    boyard 10 20 felix 100
    helsingor 20 10 ilion 200
    nox 30 30 neutral 0
    ...
    10 roads:
    # fort1 fort
    boyard helsingor
    helsingor nox
    ...
    50 marches:
    # origin destination owner size position
    boyard helsingor felix 100 0.5
    helsingor boyard ilion 10 0.1
    ...

## Internal loop

After receiving new commands from the bots, the armies are moved in the following order:
- All armies on the move (including those just ordered to move) are moved half a position on their edges.
- Colliding armies are resolved.
- All (remaining) armies are moved the second half of their movement.
- Colliding armies are resolved.

Colliding armies behave as follows:
- Armies of the same alliance ignore each other.
- Armies of different alliance annihilate each other. TODO

