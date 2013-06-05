#!/bin/bash
ROOT_FOLDER='/home/martin/share/git/cnb-dev/'
/usr/bin/epydoc -v --graph=all -o $ROOT_FOLDER''docs --html $ROOT_FOLDER''cnb/*.py $ROOT_FOLDER''cnb/modAvailable/*.py
