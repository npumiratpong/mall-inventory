#!/bin/bash

. ~/.bashrc

PROCESS_CHECKS="/root/process_checks.sh"
JOB_SCHEDULER="/root/job_runner.sh"

# Set up the cronjob
(crontab -l 2>/dev/null; echo "*/1 * * * * $PROCESS_CHECKS") | crontab -
(crontab -l 2>/dev/null; echo "05 * 05 * * $JOB_SCHEDULER") | crontab -

echo "Cronjob set up to run $PYTHON_SCRIPT_PATH every minute."