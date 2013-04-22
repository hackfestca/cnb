#!/bin/bash
ROOT_FOLDER='/home/martin/share/svn/proj/cnb'
/usr/bin/epydoc -v --graph=all -o $ROOT_FOLDER/docs --html $ROOT_FOLDER/cnb/*.py $ROOT_FOLDER/cnb/modAvailable/*.py
