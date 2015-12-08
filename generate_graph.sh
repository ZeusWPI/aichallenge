#!/bin/bash

# make tmpdir and tmpfs for storing small files and fifo's
#TMP="$(mktemp -d)"
#mount -t tmpfs none "$TMP"

# fix things
shopt -s expand_aliases
alias bc="bc -l"

generate_graph() {
    local homes="$1"

    # determine the field width and height
    local rows="$(( 2 * homes ))"
    local cols="$(( 3 * rows / 2 ))"
    local max="$(bc <<< "$homes * sqrt($rows^2 + $cols^2 + 0.0)")"
        # more than maximum indirect distance

    local i j

    # place homes at random places on the field. save some distances
    # between the homes.
    declare -a xs     # x (col) coords of the home points
    declare -a ys     # y (row) coords of the home points
    declare -a bd2m   # bird's distance squared matrix
    declare -a wdm   # walking distance squared matrix
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
        echo "$i $x -$y"
    done > points

    for (( i = 0; i < homes; i++ )); do
        for (( j = 0; j < i; j++ )); do
            wdm["$(( i * homes + j ))"]="$max"
            wdm["$(( j * homes + i ))"]="$max"
        done
        wdm["$(( i * homes + i ))"]=0.0
    done

    # create a sorted queue of distances between homes
    > mids
    > circles
    > perpends
    local narcs=0
    declare -a fa
    declare -a ta
    for (( i = 0; i < homes; i++ )); do
        for (( j = 0; j < i; j++ )); do
            echo "$(( bd2m[i * homes + j] )) $i $j"
        done
    done | sort -n | while read distance2 a b; do
        echo "considering $a $b" >&2
        local distance="$(bc <<< "sqrt($distance2) ")"
        # skip intersecting segments
        local cuts=0
        if (( xs[a] != xs[b] )); then
            local as=$(bc <<< "($((ys[a])) - $((ys[b])))/($((xs[a])) - $((xs[b])))")
            local ao=$(bc <<< "$((ys[a])) - $as*$((xs[a]))")
        fi
        for (( i = 0; i < narcs && !cuts; i++ )); do
            echo "    intersect $a $b with $((fa[i])) $((ta[i]))" >&2
            if (( a == fa[i] || a == ta[i] || b == fa[i] || b == ta[i])); then
                continue
            fi

            local boa aob
            if (( xs[a] != xs[b] )); then
                boa=$(bc <<< "($as*$((xs[fa[i]])) + $ao - $((ys[fa[i]])))*($as*$((xs[ta[i]])) + $ao - $((ys[ta[i]]))) <= 0")
            else
                boa=$(bc <<< "($((xs[fa[i]])) - $((xs[a])))*($((xs[ta[i]])) - $((xs[a]))) <= 0")
            fi
            if (( xs[fa[i]] != xs[ta[i]] )); then
                local bs=$(bc <<< "($((ys[fa[i]])) - $((ys[ta[i]])))/($((xs[fa[i]])) - $((xs[ta[i]])))")
                local bo=$(bc <<< "$((ys[fa[i]])) - $bs*$((xs[fa[i]]))")
                aob=$(bc <<< "($bs*$((xs[a])) + $bo - $((ys[a])))*($bs*$((xs[b])) + $bo - $((ys[b]))) <= 0")
            else
                aob=$(bc <<< "($((xs[a])) - $((xs[fa[i]])))*($((xs[b])) - $((xs[fa[i]]))) <= 0")
            fi
            cuts=$(bc <<< "$aob && $boa")
        done
        if test $cuts = 1; then
            echo "    intersects with $((ta[i-1])) $((fa[i-1]))" >&2
            continue
        fi

        # connect every two closest nodes if they aren't connected
        if test "$(bc <<< "${wdm[$(( a * homes + b ))]} == $max")" = 0; then

            # (indirectly) yet, or their distance would be shortened a lot by
            # the new connection.
            if test "$(bc <<< "4 * $distance < 3 * ${wdm[$(( a * homes + b ))]}")" == 0; then
                echo "    not enough of a shortcut" >&2
                continue
            fi

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
            echo "$xm -$ym" >> mids
            echo "$xp1 -$yp1 $xp2 -$yp2" >> perpends
            echo "$xp1 -$yp1 $r" >> circles
            echo "$xp2 -$yp2 $r" >> circles
            for (( i = 0; i < homes && !too_close; i++ )); do
                if (( i == a || i == b )); then continue; fi
                # other home should be "in between" a and b
                local to_p1="$(bc <<< "(${xs[$i]} - $xp1)^2 + (${ys[$i]} - $yp1)^2 < $(( bd2m[a * homes + b] )) / 2")"
                local to_p2="$(bc <<< "(${xs[$i]} - $xp2)^2 + (${ys[$i]} - $yp2)^2 < $(( bd2m[a * homes + b] )) / 2")"
                too_close="$(bc <<< "$to_p1 && $to_p2")"
            done
            if test "$too_close" == 1; then
                echo "    too close to $i" >&2
                continue
            fi
        fi

        # connect these two, update walking matrix
        echo "$((xs[a])) $((-ys[a])) $((xs[b])) $((-ys[b]))"
        fa[$narcs]=$a
        ta[$narcs]=$b
        narcs=$((narcs + 1))
        echo "    connected" >&2
        for (( i = 0; i < homes; i++ )); do
            local newd
            local bi="$((b * homes + i))"
            local ai="$((a * homes + i))"
            if test "$(bc <<< "${wdm[$ai]} < ${wdm[$bi]}")" = 1; then
                newd="$(bc <<< "${wdm[$ai]} + $distance")"
                if test "$(bc <<< "$newd < ${wdm[$bi]}")" = 1; then
                    wdm["$bi"]="$newd"
                    wdm["$(( i * homes + b ))"]="$newd"
                fi
            else
                newd="$(bc <<< "${wdm[$bi]} + $distance")"
                if test "$(bc <<< "$newd < ${wdm[$ai]}")" = 1; then
                    wdm["$ai"]="$newd"
                    wdm["$(( i * homes + a ))"]="$newd"
                fi
            fi
        done
    done > arcs

    #gnuplot:
    # plot "data.txt" with lines, "" with points 

}

main() {
generate_graph "$1"
gnuplot <<HERE
set term png
set output '$2'
plot "arcs" u 1:2:(\$3-\$1):(\$4-\$2) with vectors nohead notitle, \
     "points" using 2:3:(.3) with circles fill solid notitle, \
     "points" using 2:3:1 with labels notitle
HERE
}

