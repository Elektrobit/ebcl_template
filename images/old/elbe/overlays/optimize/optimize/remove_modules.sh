#!/bin/sh

modules_file="/etc/kernel/runtime_modules.conf"
addiitonal_modules="/optimize/modules.txt"
all_modules="/optimize/module_list"

cat $modules_file >> $all_modules
# avoid issues with missing linebreak
echo "" >> $all_modules
sed 's/_/-/g' /etc/kernel/runtime_modules.conf  >> $all_modules
echo "" >> $all_modules
cat $addiitonal_modules >> $all_modules
# delete empty lines
sed -i '/^$/d' $all_modules

cat $all_modules

if [ -f $all_modules ]; then
    if [ $(wc -l < $all_modules) -eq 0 ]; then
        echo "No modules required, delete all ..."
        rm -rf /usr/lib/modules
    else
        echo "Deleting unused modules (this may take a while) ..."
        find /usr/lib/modules -type f -name "*.ko" | grep -ivf $all_modules | xargs rm -f
    fi
else
    echo "No required modules selected, keep modules ..."
fi
