#!/bin/sh
eval `ssh-agent`
ssh-add
autossh -M 0 -o "ServerAliveInterval 30" -o "ServerAliveCountMax 3" -fN -R 10001:localhost:22 pi@130.211.204.106