#!/usr/bin/env bash

if [[ $1 == "" ]]; then
   tmux new-session -d -s yubot "python bot.py"
fi

if [[ $1 == "t" ]]; then
   python bot.py
fi

if [[ $1 == "cog" ]]; then
   cp cogs/template.py cogs/"$2".py
   nvim cogs/"$2".py
fi
