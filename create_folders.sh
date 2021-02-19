#!/bin/bash

current_dir=`pwd`;
# echo $current_dir

mkdir messages;
messages_dir=$current_dir/messages;


for committee in HR DI SC EF
do
    mkdir $messages_dir/$committee;
    mkdir $messages_dir/$committee/EB;
    # mkdir $messages_dir/$committee/EB/sent;
    # mkdir $messages_dir/$committee/EB/recv;
    # touch $messages_dir/$committee/EB/sent.json
    # touch $messages_dir/$committee/EB/recv.json
    echo "[]" | cat > $messages_dir/$committee/EB/sent.json
    echo "[]" | cat > $messages_dir/$committee/EB/recv.json
    for number in {000..500}
    do
        mkdir $messages_dir/$committee/$number/
        echo "[]" | cat > $messages_dir/$committee/$number/sent.json;
        echo "[]" | cat > $messages_dir/$committee/$number/recv.json;
    done
    for number in {900..999}
    do
        mkdir $messages_dir/$committee/$number/
        echo "[]" | cat > $messages_dir/$committee/$number/sent.json;
        echo "[]" | cat > $messages_dir/$committee/$number/recv.json;
    done
done


