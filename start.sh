#!/usr/bin/env bash

if [[ $1 == "" ]]; then
   tmux new-session -d -s yubot "python bot.py"
   tmux new-session -d -s redis-server "$0 redis-server"
fi

if [[ $1 == "redis" ]]; then
   cd /root/yubot/persist
   redis-server
fi
