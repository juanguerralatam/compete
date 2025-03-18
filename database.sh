# Copyright (c) Harbin Institute of Technology.
# Licensed under the MIT License.
#
# Source Attribution:
# The majority of this code is derived from the following sources:
# - Competeai GitHub Repository: https://github.dev/microsoft/competeai

# Function to start the servers
start_servers() {
  echo "Starting first database server"
  # Change directory to the location of your database/company_sys
  cd ./database/company_sys
  python manage.py runserver 9000 --noreload --settings=company_sys.settings.v1 &

  echo "Starting second database server"
  python manage.py runserver 9001 --noreload --settings=company_sys.settings.v2 &
}

flush_database() {
  echo "Flushing database"
  # Change directory to the location of your database/company_sys
  cd ./database/company_sys
  # Flush the database
  python manage.py flush --noinput --settings=company_sys.settings.v1
  python manage.py flush --noinput --settings=company_sys.settings.v2
}
# Function to stop the servers
stop_servers() {
  echo "Stopping database servers"
  # Find and stop the background servers (change the port numbers)
  pgrep -f "python manage.py runserver 9000" | xargs kill -9
  pgrep -f "python manage.py runserver 9001" | xargs kill -9
}

makemigrations_database() {
  echo "Makemigrating database"
  # Change directory to the location of your database/company_sys
  cd ./database/company_sys
  # Migrate the database
  python manage.py makemigrations --settings=company_sys.settings.v1
  python manage.py makemigrations --settings=company_sys.settings.v2
}

migrate_database() {
  echo "Migrating database"
  # Change directory to the location of your database/company_sys
  cd ./database/company_sys
  # Migrate the database
  python manage.py migrate --settings=company_sys.settings.v1
  python manage.py migrate --settings=company_sys.settings.v2
}

restart_database(){
  echo "Restarting database"
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
  echo "Usage: $0 [start|stop]"
  exit 1
fi