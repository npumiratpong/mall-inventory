#!/bin/bash

PROCESS_CHECKS="/root/process_checks.sh"
JOB_SCHEDULER="/root/job_runner.sh"

(crontab -l 2>/dev/null|grep -v $PROCESS_CHECKS)|crontab -
(crontab -l 2>/dev/null|grep -v $JOB_SCHEDULER)|crontab -

# Step 1: Check for running instances of uvicorn and kill them
if pgrep uvicorn > /dev/null; then
    echo "Killing running instances of uvicorn..."
    pkill uvicorn
fi

# Step 2: Remove appended variables from .bashrc file
sed -i '/# This is path for user application/d' ~/.bashrc
sed -i '/TYPE_ENV="prod"/d' ~/.bashrc
sed -i '/BASE_PATH="\/var\/backend\/mall-inventory"/d' ~/.bashrc
sed -i '/APP_PATH="$BASE_PATH\/app"/d' ~/.bashrc
sed -i '/SCHEDULER_PATH="$BASE_PATH\/job_scheduler"/d' ~/.bashrc

# Step 3: Remove installed files and directories
rm -rf /var/backend/mall-inventory
rm /root/job_runner.sh
rm /root/process_checks.sh
rm /root/setup_crons.sh

# Step 4: Inform user
echo "Package has been uninstalled."