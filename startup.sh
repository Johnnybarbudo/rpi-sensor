#!/bin/sh
eval `ssh-agent`
ssh-add
autossh -M 0 -o "ServerAliveInterval 30" -o "ServerAliveCountMax 3" -fN -R 10010:localhost:22 simon@104.199.69.122
export GOOGLE_APPLICATION_CREDENTIALS="serviceaccount_pubsub.json"
