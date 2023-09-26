#!/usr/bin/env bash

for i in *;do
    if [ -d $i ];then
        DIR="$PWD/$i"
        FILE="$DIR/install.inf"
        SUBDIR="$(grep 'subdir' $FILE)"
        NAME="${SUBDIR/subdir=/}"
        echo "$NAME"

        mkdir -p data/langpy/pt_BR/LC_MESSAGES
        pygettext3 -d data/langpy/pt_BR/LC_MESSAGES/$NAME "$DIR"

    fi
done
