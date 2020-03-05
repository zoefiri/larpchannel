#!/usr/bin/env bash

if [[ $1 == "" ]]; then
   tmux new-session -d -s redis-server "cd persist && redis-server"
   sleep .4
   tmux new-session -d -s yubot "python bot.py"
fi
