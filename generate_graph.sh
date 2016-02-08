#!/bin/bash

# make tmpdir and tmpfs for storing small files and fifo's
#TMP="$(mktemp -d)"
#mount -t tmpfs none "$TMP"

# fix things
shopt -s expand_aliases
alias bc="bc -l"

intersect() {
    local xa0="$1" ya0="$2" xa1="$3" ya1="$4" xb0="$5" yb0="$6" xb1="$7" yb1="$8"
    local boa aob
    if (( xa0 != xa1 )); then
        local as=$(bc <<< "($ya0 - $ya1)/($xa0 - $xa1)")
        local ao=$(bc <<< "$ya0 - $as*$xa0")
        boa=$(bc <<< "($as*$xb0 + $ao - $yb0)*($as*$xb1 + $ao - $yb1) <= 0")
    else
        boa=$(bc <<< "($xb0 - $xa0)*($xb1 - $xa0) <= 0")
    fi
    if (( xb0 != xb1 )); then
        local bs=$(bc <<< "($yb0 - $yb1)/($xb0 - $xb1)")
        local bo=$(bc <<< "$yb0 - $bs*$xb0")
        aob=$(bc <<< "($bs*$xa0 + $bo - $ya0)*($bs*$xa1 + $bo - $ya1) <= 0")
    else
        aob=$(bc <<< "($xa0 - $xb0)*($xa1 - $xb0) <= 0")
    fi
    echo $(bc <<< "$aob && $boa")
}

generate_graph() {
    # uses:
    # - homes: the number of nodes the graph should have
    #
    # overwrites:
    # - xs: with the x coordinates of home $i, 0 < $i < $homes
    # - ys: with the y coordinates of homes $i, 0 < $i < $homes
    # - roads: with the number of edges drawn
    # - te: with the beginning homes of edge $i, 0 < $i < $roads
    # - fe: with the ending homes of edge $i, 0 < $i < $roads
    echo "Generating Graph" >&2

    # determine the field width and height
    local rows="$(( 2 * homes ))"
    local cols="$(( 3 * rows / 2 ))"

    local i j

    # place homes at random places on the field. save some distances
    # between the homes.
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
        echo "adding point $i: $x $y"
    done

    for (( i = 0; i < homes; i++ )); do
        for (( j = 0; j < i; j++ )); do
            con["$(( i * homes + j ))"]=0
            con["$(( j * homes + i ))"]=0
        done
        con["$(( i * homes + i ))"]=1
    done

    # initializing the number of roads
    roads=0
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
            local too_close=0
            local xm="$(bc <<< "$(( xs[a] + xs[b] )) / 2")"
            local ym="$(bc <<< "$(( ys[a] + ys[b] )) / 2")"
            local xp1="$(bc <<< "$xm - $(( ys[b] - ys[a] )) / 2")"
            local yp1="$(bc <<< "$ym + $(( xs[b] - xs[a] )) / 2")"
            local xp2="$(bc <<< "$xm + $(( ys[b] - ys[a] )) / 2")"
            local yp2="$(bc <<< "$ym - $(( xs[b] - xs[a] )) / 2")"
            local r="$(bc <<< "sqrt($(( bd2m[a * homes + b] )) / 2)")"
            for (( i = 0; i < homes && !too_close; i++ )); do
                if (( i == a || i == b )); then continue; fi
                # other home should be "in between" a and b
                local to_p1="$(bc <<< "(${xs[$i]} - $xp1)^2 + (${ys[$i]} - $yp1)^2 < $(( bd2m[a * homes + b] )) / 2")"
                local to_p2="$(bc <<< "(${xs[$i]} - $xp2)^2 + (${ys[$i]} - $yp2)^2 < $(( bd2m[a * homes + b] )) / 2")"
                too_close="$(bc <<< "$to_p1 && $to_p2")"
            done
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
        for (( i = 0; i < homes; i++ )); do
            local connected="$(( con[a*homes + i] || con[b*homes + i] ))"
            con[$(( a*homes + i ))]="$connected"
            con[$(( i*homes + a ))]="$connected"
            con[$(( b*homes + i ))]="$connected"
            con[$(( i*homes + b ))]="$connected"
        done
    done

    #gnuplot:
    # plot "data.txt" with lines, "" with points 

}

main() {
    # Expects as parameters a list of player names zipped with the
    # location of their bot executables.
    declare -a players
    declare -a botboxes
    generate_players "$@"
    local nplayers="${#players[@]}"

    declare -a writeprocs
    declare -a outputs
    local i
    for (( i = 0; i < nplayers; i++ )); do
        echo "$i" > "${botboxes[$i]}/stdin" &

        turnprocs[$i]="$!"
    done

    # TODO

    declare -a xs
    declare -a ys
    local roads
    declare -a fe
    declare -a te
    #generate_graph

}

generate_players() {
    local n=0
    while (( $# >= 2 )); do

        players[$n]="$1"
        botboxes[$n]="$(isolate --box-id="$n" --init)/box"
        mkfifo "${botboxes[$n]}/stdin"
        mkfifo "${botboxes[$n]}/stdout"
        mkfifo "${botboxes[$n]}/stderr"
        cp "$2" "${botboxes[$n]}/"
        isolate --box-id="$n"                         \
                --stdin="${botboxes[$n]}/stdin"   \
                --stdout="${botboxes[$n]}/stdout" \
                --stderr="${botboxes[$n]}/stderr" \
                --processes=1                         \
                --run "${2##*/}" > /dev/null 2>&1     &
        shift 2
        i="$((n + 1))"
    done
}

plot() {
gnuplot <<HERE
set term png size 3000,3000
set output '$1'
plot \
     "arcs" using 1:2:(\$3-\$1):(\$4-\$2) with vectors nohead notitle, \
     "points" using 2:3:(0.3) with circles fill solid notitle, \
     "points" using 2:3:1 with labels notitle
HERE
}

     #"perpends" using 1:2:(\$3-\$1):(\$4-\$2) with vectors nohead notitle, \
     #"circles" with circles notitle
     #"mids" with points notitle, \
