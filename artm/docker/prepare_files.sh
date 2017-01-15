#!/bin/bash

cp ../data/dict.filtered .
cp ../data/big_model.artm.mtx .
cp ../data/insception-classes.tsv .

jupyter nbconvert --to python ../notebooks/model_application.ipynb --output $(pwd)/model_application.py
cp ../notebooks/utils.py .
