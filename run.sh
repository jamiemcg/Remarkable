#!/bin/bash
foldername=`dirname $(readlink -f $0)`
PYTHONPATH=$foldername/remarkable:$foldername/remarkable_lib exec $foldername/bin/remarkable "$@"
