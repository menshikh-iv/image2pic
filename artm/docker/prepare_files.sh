#!/bin/bash

cp ../models/big_model.artm.mtx .
cp ../resourses/insception-classes.tsv .

jupyter nbconvert --to python ../workspace/model_application.ipynb --output $(pwd)/model_application.py
cp ../workspace/utils.py .
