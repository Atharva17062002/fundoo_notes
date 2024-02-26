#!/bin/bash

if [ "$1" == "user" ];then
flask --app main:user run --debug --port 5000
elif [ "$1" == "notes" ];then
flask --app main:notes run --debug --port 8000
elif [ "$1" == "label" ];then
flask --app main:label run --debug --port 7010
else
echo "Command not found"
fi
