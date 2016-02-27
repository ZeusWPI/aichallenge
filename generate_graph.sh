#!/bin/bash

# make tmpdir and tmpfs for storing small files and fifo's
#TMP="$(mktemp -d)"
#mount -t tmpfs none "$TMP"

# fix things
shopt -s expand_aliases
alias bc="bc -l"

intersect() {
    bc <<<"
        xa0 = $1; ya0 = $2; xa1 = $3; ya1 = $4;
        xb0 = $5; yb0 = $6; xb1 = $7; yb1 = $8;
        if (xa0 != xa1) {
            as = (ya0 - ya1) / (xa0 - xa1);
            ao = ya0 - as*xa0;
            boa = ((as*xb0 + ao - yb0) * (as*xb1 + ao - yb1) <= 0);
        } else {
            boa = ((xb0 - xa0) * (xb1 - xa0) <= 0);
        }
        if (xb0 != xb1) {
            bs = (yb0 - yb1) / (xb0 - xb1);
            bo = yb0 - bs*xb0;
            aob = ((bs*xa0 + bo - ya0) * (bs*xa1 + bo - ya1) <= 0);
        } else {
            aob = ((xa0 - xb0) * (xa1 - xb0) <= 0);
        }
        aob && boa;
    "
}

names() {
    sort -R <<HERE
miou
miaou
miauw
meow
mraaaaaw
purrr
prrrrrrrr
GSHSHSHSHSHSHSS
mraaAAW?
HERE
}

forts() {
    sort -R <<HERE
aberwyvern
alnwick
amon-sul
anvard
arundel
ashford
banefort
barad-dur
beaumaris
belvoir
blandings
blarney
bowsers-castle
boyard
bran
caernarfon
caerphilly
cair-paravel
caladan
camelot
carcasonne
carignano
castamere
casterly-rock
castle-aaaaaaaaarrrggh
castle-black
castlevania
chambord
conway
deepwood-mottle
disney-castle
dol-gulder
dover
dragonstone
dreadfort
duckula
eilean-donan
eyrie
floors
foix
gaillard
glagnorra
gormenghast
grayskull
greyguard
greywater-watch
grimm
harrenhal
helsingor
highgarden
highpoint
hogwarts
hornburg
hyrule-castle
ironrath
isengard
karhold
katz-kastle
krak-des-chevaliers
last-hearth
marlinspike
minas-morgul
moat-cailin
montaillou
montsegur
neuschwanstein
nightfort
nox
otranto
pyke
redfort
red-keep
riverrun
runestone
sant-angelo
sao-jorge
seagard
skyreach
starfall
stokeworth
storms-end
summerhall
sunspear
the-citadel
the-dark-tower
tintagel
ton-towers
torquilstone
torrhens-square
trim
twins
urquhart
versailles
windsor
winterfell
wolfenstein
HERE
}

generate_graph() {
    # uses:
    # - players: the number of nodes the graph should have
    #
    # overwrites:
    # - xs: with the x coordinates of home $i, 0 < $i < $homes
    # - ys: with the y coordinates of homes $i, 0 < $i < $homes
    # - roads: with the number of edges drawn
    # - te: with the beginning homes of edge $i, 0 < $i < $roads
    # - fe: with the ending homes of edge $i, 0 < $i < $roads

    local homes="$(( 10 + players * players + RANDOM%(2 * wanderlust + 1) - wanderlust ))"
    echo "$homes forts:"
    # determine the field width and height
    local rows="$(( 2 * homes ))"
    local cols="$(( 3 * rows / 2 ))"

    local i j

    # place homes at random places on the field. save some distances
    # between the homes.
    declare -a xs
    declare -a ys
    declare -a fortnames
    declare -a bd2m   # bird's distance squared matrix
    declare -a con    # are two points connected?
    for (( i = 0; i < homes; i++ )); do
        while true; do
            local x="$(( RANDOM % cols ))"
            local y="$(( RANDOM % rows ))"
            local too_close=0
            for (( j = 0; j < i && !too_close; j++ )); do
                local dx2="$(( (x - xs[j]) ** 2 ))"
                local dy2="$(( (y - ys[j]) ** 2 ))"
                if (( dx2 < 8 && dy2 < 8 )); then
                    too_close=1
                else
                    bd2m["$(( i * homes + j ))"]="$(( dx2 + dy2 ))"
                    bd2m["$(( j * homes + i ))"]="$(( dx2 + dy2 ))"
                fi
            done
            if (( !too_close )); then break; fi
        done
        xs["$i"]="$x"
        ys["$i"]="$y"
        local fort player armysize
        read fort player armysize
        fortnames["$i"]="$fort"
        echo "$fort $x $y ${player:-neutral} ${armysize:-0}"
    done < <(echo "$playernames" | sed 's/$/\t100/' | paste <(forts) -)

    for (( i = 0; i < homes; i++ )); do
        for (( j = 0; j < i; j++ )); do
            con["$(( i * homes + j ))"]=0
            con["$(( j * homes + i ))"]=0
        done
        con["$(( i * homes + i ))"]=1
    done

    # initializing the number of roads
    local roads=0
    declare -a te
    declare -a fe
    for (( i = 0; i < homes; i++ )); do
        # create a (sorted) queue of distances between homes
        for (( j = 0; j < i; j++ )); do
            echo "$(( bd2m[i * homes + j] )) $i $j"
        done
    done | sort -n | while read distance2 a b; do
        echo -n "considering connecting $a and $b" >&2
        local distance="$(bc <<< "sqrt($distance2) ")"
        # skip intersecting segments
        local cuts=0
        for (( i = 0; i < roads && !cuts; i++ )); do
            if (( a == fe[i] || a == te[i] || b == fe[i] || b == te[i])); then
                continue
            fi
            cuts=$(intersect $((xs[a])) $((ys[a])) $((xs[b])) $((ys[b])) $((xs[fe[i]])) $((ys[fe[i]])) $((xs[te[i]])) $((ys[te[i]])))
        done
        if test $cuts = 1; then
            echo "           intersects with $((te[i-1])) to $((fe[i-1]))" >&2
            continue
        fi

        # connect every two closest nodes if they aren't connected
        if (( con[a * homes + b] )); then
            echo -n "    old" >&2

            # if the new connection passes too close to another home, skip
            # it.
            local too_close="$(bc <<<"
                too_close = 0;
                xm = $((xs[a] + xs[b])) / 2;
                ym = $((ys[a] + ys[b])) / 2;
                xp1 = xm - $((ys[b] - ys[a])) / 2;
                yp1 = ym + $((xs[b] - xs[a])) / 2;
                xp2 = xm + $((ys[b] - ys[a])) / 2;
                yp2 = ym - $((xs[b] - xs[a])) / 2;
                r = sqrt($((bd2m[a * homes + b])) / 2);
                for ( i = 0 ; i < homes && !too_close ; i++) {
                    if (i == a || i == b) {
                        continue;
                    }
                    /* other home should be in between a and b */
                    to_p1 = ((${xs[$i]} - xp1)^2 + (${ys[$i]} - yp1)^2 < $((bd2m[a * homes + b])) / 2);
                    to_p2 = ((${xs[$i]} - xp2)^2 + (${ys[$i]} - yp2)^2 < $((bd2m[a * homes + b])) / 2);
                    too_close = to_p1 && to_p2;
                }
                too_close
            ")"
            if test "$too_close" == 1; then
                echo "    too close to point $((i - 1))" >&2
                continue
            fi
        else
            echo -n "    new" >&2
        fi

        # connect these two, update walking matrix
        fe[$roads]=$a
        te[$roads]=$b
        roads=$((roads + 1))
        echo "    connected" >&2
        echo "${fortnames[$a]} ${fortnames[$b]}"
        for (( i = 0; i < homes; i++ )); do
            local connected="$(( con[a*homes + i] || con[b*homes + i] ))"
            con[$(( a*homes + i ))]="$connected"
            con[$(( i*homes + a ))]="$connected"
            con[$(( b*homes + i ))]="$connected"
            con[$(( i*homes + b ))]="$connected"
        done
    done | sort -r | tee >(wc -l | sed 's/$/ roads:/') | tac

}

wanderlust="$1"
players="$2"
if [ -z "$players" ]; then
    # expect players on stdin
    playernames="$(cat)"
    players="$(echo "$playernames" | wc -l)"
else
    # generate players
    playernames="$(names | head -$players)"
fi
generate_graph
echo "0 marches:"
