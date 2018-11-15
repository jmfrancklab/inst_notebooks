#!/bin/bash
b=`basename $1 .ipynb`
jupyter nbconvert --to script $b.ipynb
sed -i 's/^\(# \)In\[.*/\1/' $b.py
