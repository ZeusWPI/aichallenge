#!/bin/bash

# make tmpdir and tmpfs for storing small files and fifo's
#TMP="$(mktemp -d)"
#mount -t tmpfs none "$TMP"

# fix things
alias bc="bc -l"

intersect() {
    # http://stackoverflow.com/questions/4977491/determining-if-two-line-segments-intersect?lq=1
    local xa0="$1" ya0="$2" xa1="$3" ya1="$4" xb0="$5" yb0="$6" xb1="$7" yb1="$8"
    local d=$(bc <<< "xb1 * ya1 - xa1 * yb1")
    if test "$(bc <<< "$d == 0")" = 1; then
        # parallel
        true
    else
        local s=$(bc <<< " (  ($xa0 - $xb0)*$ya1 - ($ya0 - $yb0)*$xa1 )/$d")
        local t=$(bc <<< "-( -($xa0 - $xb0)*$yb1 + ($ya0 - $yb0)*$xb1 )/$d")
        return $(bc <<< "0 <= $s && $s <= 1 && 0 <= $t && $t <= 1")
    fi
}

generate_graph() {
    local homes="$1"

    # determine the field width and height
    local rows="$(( 2 * homes ))"
    local cols="$(( 3 * rows / 2 ))"
    local max="$(bc <<< "$homes * sqrt($rows^2 + $cols^2 + 0.0)")"
        # more than maximum indirect distance

    local i j
    declare -a field  # TODO for debug printing

    # place homes at random places on the field. save some distances
    # between the homes.
    declare -a xs     # x (col) coords of the home points
    declare -a ys     # y (row) coords of the home points
    declare -a bd2m   # bird's distance squared matrix
    declare -a wdm   # walking distance squared matrix
    echo -e "punt:\t(row,\tcol)"
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
        field["$(( y*cols + x ))"]=1
        echo -e "$i:\t(${y},\t${x})"
    done
    echo

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
    for (( i = 0; i < homes; i++ )); do
        for (( j = 0; j < i; j++ )); do
            echo "$(( bd2m[i * homes + j] )) $i $j"
        done
    done | sort -n | while read distance2 a b; do
        local distance="$(bc <<< "sqrt($distance2 + 0.0)")"
        # skip intersecting segments
        # TODO

        # connect every two closest nodes if they aren't connected
        #if test "$(bc <<< "${wdm[$(( a * homes + b ))]} == $max")" = 0; then
            echo "($a, $b) is a connection, testing" >&2
            # (indirectly) yet, or their distance would be shortened a lot by
            # the new connection.
            #if test "$(bc <<< "2 * $distance < 1 * ${wdm[$(( a * homes + b ))]}")" == 0; then
            #    continue
            #fi

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
                echo "skipping $a to $b for $i" >&2
                continue
            fi
        #fi

        # connect these two, update walking matrix
        echo "$((xs[a])) $((-ys[a])) $((xs[b])) $((-ys[b]))"
        echo "connected $a and $b" >&2
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
    done > data.txt
    #gnuplot:
    # plot "data.txt" with lines, "" with points 

    echo -n "  "
    for (( j = 0; j < cols; j++ )); do
        echo -n " $(( j % 10 ))"
    done
    echo
    for (( i = 0; i < rows; i++ )); do
        echo -n " $(( i % 10 ))"
        for (( j = 0; j < cols; j++ )); do
            echo -n " $(( field[i*cols + j] + 0 ))" | tr '01' '-X'
        done
        echo
    done
}

