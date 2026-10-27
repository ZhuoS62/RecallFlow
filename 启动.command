#!/bin/zsh
set -eu
cd -- "${0:A:h}/server"
exec docker compose -f docker-compose.yaml -f docker-compose.local.yaml up -d
