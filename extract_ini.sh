#!/usr/bin/env bash

for i in *;do

    if [ -d $i ];then

        FILE="$PWD/$i/install.inf"
        CAPTION="$(grep 'caption=' $FILE)"
        SUBDIR="$(grep 'subdir=' $FILE)"
        FOLDER="${SUBDIR/subdir=/}"

        mkdir -p "langmenu/$FOLDER"
        echo '[menu]' > "langmenu/$FOLDER/pt_BR.ini"

        echo "$(awk -F'\' '{print $1"="}' <<< $CAPTION|sed 's|caption=||'|uniq)" >> "langmenu/$FOLDER/pt_BR.ini"

        if [ "$(cut -d'\' -f2 <<< $CAPTION)" ];then
            echo "$(awk -F'\' '{print $2"="}' <<< $CAPTION|uniq)" >> "langmenu/$FOLDER/pt_BR.ini"
        fi
        if [ "$(cut -d'\' -f3 <<< $CAPTION)" ];then
            echo "$(awk -F'\' '{print $3"="}' <<< $CAPTION|uniq)" >> "langmenu/$FOLDER/pt_BR.ini"
        fi

    fi
done
