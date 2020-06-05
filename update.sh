#!/bin/sh

# Shell script for daily update of database and dashboard
#
# Run with no arguments:
#   ./update.sh

./download_metadata.py || exit 1
./generate_dashboard.py >| index.html || exit 1

d=`date +'%Y-%m-%d'`
if [ -z "$GITHUB_ACTIONS" ] ; then
  msg="🔄 ${d} update"
else
  msg="🤖 🔄 ${d} automated update"
fi

git commit data/* index.html -m "${msg}" && git push
