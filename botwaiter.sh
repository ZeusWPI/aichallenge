#!/bin/bash

inback() {
    {
        sleep "$3"
        echo "$2" > "$1"
    } &
}

per_time() {
    local n="$1"
    local timeout="$2"
    shift 2
    head -n "$n" sema &
    local runner="$!"
    local i
    for (( i = 1; i <= n; i++ )); do
        head -1 "${!i}" | sed "s/^/$i /" > sema &
        echo "$!"
    done | {
        sleep "$timeout"
        kill "$runner"
        xargs kill
    } 2> /dev/null
}

main() {
    mkfifo fifo1 fifo2 fifo3 sema
    inback fifo1 "message1" 2
    inback fifo2 "message2" 4
    inback fifo3 "message3" 6
    per_time 3 5 fifo1 fifo2 fifo3
    wait
    rm fifo1 fifo2 fifo3 sema
}

get_output() {
    cat my_lovely_in &
    proc="$!"
    sleep "$1"
    if ps -p "$proc" > /dev/null; then
        # CHEATER! No turn for you!
        kill "$proc"
    fi
    wait "$proc"
}

