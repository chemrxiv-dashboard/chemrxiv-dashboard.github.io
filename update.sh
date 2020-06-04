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
if [ -z "$GITHUB_TOKEN" ] ; then
  msg="🔄 ${d} update"
else
  msg="🤖 🔄 ${d} automated update"
fi

git commit data/* index.html -m "${msg}" && git push
