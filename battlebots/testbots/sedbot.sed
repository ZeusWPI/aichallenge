#!/bin/sed
/forts/ {
    i\
? commands:
    x
    s/.*/0/
    x
    d
}
/roads/ {
    x
    s/0/1/
    x
    d
}
/marches/ {
    x
    i\
end
    s/1/0/
    x
    d
}
x
s/1/0/
t then
s/0/1/
t else
: end
x
d

: else
s/1/0/
b end

: then
x
s/$/ 1/p
s/\(.*\) \(.*\) 1/\2 \1 1/p
x
s/0/1/
b end
