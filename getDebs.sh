#!/bin/bash

globDepList=()

containsElement () {
  local seeking="$1"
  local found=0

  for element in "${globDepList[@]}"
  do
    if [[ $element == "$seeking" ]]
    then
        found=1
        break
    fi
  done
  echo $found
}

ListLibDeps()
{
    local contElem=0
    local curDep="$1"
    local depLists=$(apt-cache depends ${curDep} | grep -E 'Depends|Recommends|Suggests' | cut -d ':' -f 2,3 | sed -e s/'<'/''/ -e s/'>'/''/)
    # depLists=$(echo ${depLists} | grep -E 'Depends|Recommends|Suggests')
    # depLists=$(echo ${depLists} | cut -d ':' -f 2,3)
    # depLists=$(echo ${depLists} | sed -e s/'<'/''/ -e s/'>'/''/)

    # for i in $(apt-cache depends ${curDep} | grep -E 'Depends|Recommends|Suggests' | cut -d ':' -f 2,3 | sed -e s/'<'/''/ -e s/'>'/''/);
    for j in ${depLists};
        do
        contElem=$(containsElement $j)
        if [ $contElem -eq 0 ]
        then
        globDepList+=("$j")
        echo searching for $j
        ListLibDeps $j
        apt-get download $j 2>>errors.txt
        fi
    done
    apt-get download ${curDep} 2>>errors.txt
}

args=("$@")
for ((i=0; i < $#; i++))
{
    ListLibDeps "${args[$i]}"
}
for value in "${globDepList[@]}"
do
    echo $value
done

# for i in $(apt-cache depends python | grep -E 'Depends|Recommends|Suggests' | cut -d ':' -f 2,3 | sed -e s/'<'/''/ -e s/'>'/''/); do sudo apt-get download $i 2>>errors.txt; done
#    echo "argument $((i+1)): ${args[$i]}"
