#!/bin/sh

# Shell script for daily update of database and dashboard
#
# Run with no arguments:
#   ./update.sh

error() {
  exit 1
}

./download_metadata.py || exit
./generate_dashboard.py >| index.html || exit

d=`date +'%Y-%m-%d'`
git commit data/* index.html -m "🔄 ${d} update" && git push
