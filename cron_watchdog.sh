#!/bin/bash
cd /kunden/homepages/6/d420749223/htdocs/Diviq/DicordBots/Diviq-sos-bot
if ! pgrep -f "python.*bot.py" > /dev/null; then
    echo "$(date) [watchdog] bot not running — starting" >> logs/watchdog.log
    nohup python3 -u bot.py > /dev/null 2>&1 &
    disown
else
    echo "$(date) [watchdog] bot is running" >> logs/watchdog.log
fi
