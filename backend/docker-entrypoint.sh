#!/bin/sh
set -e

# /app/storage is meant to be a persistent volume (admin edits: project
# catalog and uploaded images). On its first start it is empty, so it gets
# the catalog and images shipped with the code. Later starts leave it alone.
if [ ! -f /app/storage/projects.json ]; then
  cp -r /app/seed/storage/. /app/storage/
fi
mkdir -p /app/storage/uploads

exec "$@"
