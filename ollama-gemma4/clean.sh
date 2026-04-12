#!/bin/bash
cd "$(dirname "$0")"
set -e

echo "This will stop all containers AND delete all model data."
read -p "Are you sure? [y/N] " confirm
if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "Aborted."
    exit 0
fi

echo "Stopping and removing containers + volumes..."
docker compose down -v
echo "Done. All model data has been removed."
