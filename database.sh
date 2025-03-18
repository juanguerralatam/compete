#!/bin/bash
# Copyright (c) Harbin Institute of Technology.
# Licensed under the MIT License.
#
# Source Attribution:
# The majority of this code is derived from the following sources:
# - Competeai GitHub Repository: https://github.dev/microsoft/competeai

# Function to start the servers
start_servers() {
  echo "Starting first database server"
  cd /home/juan/Documents/compete/database
  python manage.py runserver 9000 --noreload --settings=database.settings.v1 &
  echo "Starting second database server"
  python manage.py runserver 9001 --noreload --settings=database.settings.v2 &
}

# Function to flush the databases
flush_database() {
  echo "Flushing databases"
  cd /home/juan/Documents/compete/database
  python manage.py flush --noinput --settings=database.settings.v1
  python manage.py flush --noinput --settings=database.settings.v2
}

# Function to stop the servers
stop_servers() {
  echo "Stopping database servers"
  pkill -f "python manage.py runserver 9000"
  pkill -f "python manage.py runserver 9001"
}

# Function to make migrations
makemigrations_database() {
  echo "Making migrations"
  cd /home/juan/Documents/compete/database
  python manage.py makemigrations --settings=database.settings.v1
  python manage.py makemigrations --settings=database.settings.v2
}

# Function to migrate the databases
migrate_database() {
  echo "Migrating databases"
  cd /home/juan/Documents/compete/database
  python manage.py migrate --settings=database.settings.v1
  python manage.py migrate --settings=database.settings.v2
}

# Function to restart the databases
restart_database() {
  echo "Restarting databases"
  stop_servers
  flush_database
  start_servers
}

# Check the argument provided to the script
if [ "$1" == "start" ]; then
  start_servers
elif [ "$1" == "stop" ]; then
  stop_servers
elif [ "$1" == "flush" ]; then
  flush_database
elif [ "$1" == "makemigrations" ]; then
  makemigrations_database
elif [ "$1" == "migrate" ]; then
  migrate_database
elif [ "$1" == "restart" ]; then
  restart_database
else
  echo "Usage: $0 [start|stop|flush|makemigrations|migrate|restart]"
  exit 1
fi