#!/bin/bash

for file1 in $(find . -name '*.itp') ; do 
	file2=${file1}2
	echo $file2
	
	DIFF=$(diff $file1 $file2)
	#echo $DIFF
	if [ "$DIFF" != "" ]
	then
	    echo "      file $file1 not the same"
	fi
done