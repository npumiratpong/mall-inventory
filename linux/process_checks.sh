#!/bin/bash

. ~/.bashrc


cd $APP_PATH

echo $APP_PATH
export TYPE_ENV="prod"

#Set the path to your command
PROCESS_NAME="uvicorn"
PROCESS_COMMAND="uvicorn main:app --host localhost --port 8000 --reload"

if pgrep -f "$PROCESS_NAME" > /dev/null;
then
    echo "The $PROCESS_NAME is running..."
else
    echo "The $PROCESS_NAME is not running. Restarting ..."
    $PROCESS_COMMAND 2> errorOutput-$(date +%Y-%m-%d_%H-%M-%S).log > output-$(date +%Y-%m-%d_%H-%M-%S).log &
fi