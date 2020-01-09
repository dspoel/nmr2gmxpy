#!/bin/bash

for str_name in $(find . -name '*.str') ; do 
        #name=${filename##*/}
        base=${str_name%_mr.str}
	top_name=${base}.top
	echo $base
	python ./nmr_to_gromacs.py -m $str_name -p $top_name -v
	python nmrstar_to_gromacs.py -m $str_name -p $top_name -v
done