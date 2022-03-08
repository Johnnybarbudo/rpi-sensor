#!/bin/sh
eval `ssh-agent`
ssh-add
autossh -M 0 -o "ServerAliveInterval 30" -o "ServerAliveCountMax 3" -fN -R 10001:localhost:22 pi@192.168.1.133
export GOOGLE_APPLICATION_CREDENTIALS="serviceaccount_pubsub.json"
