#!/bin/bash

# make tmpdir and tmpfs for storing small files and fifo's
#TMP="$(mktemp -d)"
#mount -t tmpfs none "$TMP"

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
    declare -a wd2m   # walking distance squared matrix
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
            wd2m["$(( i * homes + j ))"]="$max"
            wd2m["$(( j * homes + i ))"]="$max"
        done
        wd2m["$(( i * homes + i ))"]=0.0
    done

    # create a sorted queue of distances between homes
    for (( i = 0; i < homes; i++ )); do
        for (( j = 0; j < i; j++ )); do
            echo "$(( bd2m[i * homes + j] )) $i $j"
        done
    done | sort -n | while read distance2 a b; do
        # connect every two closest nodes if they aren't connected
        # (indirectly) yet, or their distance would be shortened a lot by
        # the new connection.
        local distance="$(bc <<< "sqrt($distance2 + 0.0)")"
        if test "$(bc <<< "2 * $distance < 1 * ${wd2m[$(( a * homes + b ))]}")" = 1; then
            # connect these two, update walking matrix
            echo "$((xs[a])) $((-ys[a]))"
            echo "$((xs[b])) $((-ys[b]))"
            echo # output for gnuplot:
            for (( i = 0; i < homes; i++ )); do
                local newd
                local bi="$((b * homes + i))"
                local ai="$((a * homes + i))"
                if test "$(bc <<< "${wd2m[$ai]} < ${wd2m[$bi]}")" = 1; then
                    newd="$(bc <<< "${wd2m[$ai]} + $distance")"
                    if test "$(bc <<< "$newd < ${wd2m[$bi]}")" = 1; then
                        wd2m["$bi"]="$newd"
                        wd2m["$(( i * homes + b ))"]="$newd"
                    fi
                else
                    newd="$(bc <<< "${wd2m[$bi]} + $distance")"
                    if test "$(bc <<< "$newd < ${wd2m[$ai]}")" = 1; then
                        wd2m["$ai"]="$newd"
                        wd2m["$(( i * homes + a ))"]="$newd"
                    fi
                fi
            done
        fi
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

