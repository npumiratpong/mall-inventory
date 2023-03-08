#!/bin/bash

. ~/.bashrc


cd $SCHEDULER_PATH

echo `pwd`

export TYPE_ENV="prod"

#Set the path to your command

PROCESS_COMMAND=main.py


echo "Running Job Scheduler"
./$PROCESS_COMMAND 2> errorOutput-$(date +%Y-%m-%d_%H-%M-%S).log > output-$(date +%Y-%m-%d_%H-%M-%S).log &
