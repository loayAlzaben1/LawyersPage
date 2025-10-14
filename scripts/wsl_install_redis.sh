#!/usr/bin/env bash
# For WSL Ubuntu: install redis-server and start it
set -e
if ! command -v redis-server >/dev/null 2>&1; then
  sudo apt update
  sudo apt install -y redis-server
fi
sudo service redis-server start
sudo service redis-server status
