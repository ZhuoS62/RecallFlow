#!/bin/zsh
set -eu
cd -- "${0:A:h}/server"
exec python3 configure_ark_local.py
