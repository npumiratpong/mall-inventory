#!/bin/bash

# Set environment variables in ~/.bashrc
echo '#This is path for user application' >> ~/.bashrc
echo 'TYPE_ENV="prod"' >> ~/.bashrc
echo 'BASE_PATH="/var/backend/mall-inventory"' >> ~/.bashrc
echo 'APP_PATH="$BASE_PATH/app"' >> ~/.bashrc
echo 'SCHEDULER_PATH="$BASE_PATH/job_scheduler"' >> ~/.bashrc

# Reload ~/.bashrc
source ~/.bashrc

# Unzip tar package to $BASE_PATH
tar -xvf inventory_.tar -C $BASE_PATH

# Move files to /root/ and make them executable
mv job_runner.sh /root/
mv process_checks.sh /root/
mv setup_crons.sh /root/
chmod +x /root/job_runner.sh
chmod +x /root/process_checks.sh
chmod +x /root/setup_crons.sh

# Run the three files in order
/root/setup_crons.sh
/root/process_checks.sh
/root/job_runner.sh