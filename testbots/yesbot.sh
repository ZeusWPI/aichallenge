#! /bin/bash

yes | sed "s/y/\n#TEST\n0 marches:/" &
cat - > /dev/null
