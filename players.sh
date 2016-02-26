#! /bin/sh
# Get list of players in a map
cut -d ' ' -f 4 $1 | grep -Ev '(^$)|(neutral)' | sort | uniq
