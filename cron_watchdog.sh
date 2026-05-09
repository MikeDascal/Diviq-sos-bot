#!/bin/bash
cd /kunden/homepages/6/d420749223/htdocs/Diviq/DicordBots/Diviq-sos-bot
if ! pgrep -f "python.*bot.py" > /dev/null; then
    nohup python3 -u bot.py >> logs/bot.log 2>&1 &
    disown
fi
