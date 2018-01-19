#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8
#
# Mongueimers bot para nuestras cosas de Steam

from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import Filters
from telegram import bot
from urllib2 import Request, urlopen, URLError
import logging
import json

player_summary = 'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=%s&steamids=%d&format=json'
app_data = 'http://store.steampowered.com/api/appdetails?appids=%d'

try:
    with open('config.json', 'r') as f:
        config = json.load(f)

    telegram_api_key = config['API']['telegram']
    enabled_chat = config['chat_id']
except IOError, e:
    print('Unable to start the bot. Don\'t have config file')
    exit()
except KeyError, e:
    print('Unable to start the bot. Don\'t have telegram key')
    exit()

updater = Updater(token=telegram_api_key)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def alguien(bot, update):
    with open('now_playing.md', 'r') as f:
        text_response = f.read().decode('utf-8')
    with open('player.md', 'r') as f:
        now_player = f.read().decode('utf-8')
    num_gamers = 0
    try:
        steam_key = config['API']['steam']
    except KeyError, e:
        print('Unable to start the bot, no steam API key')
    try:
        for player in config['players']:
            player_url = player_summary % (steam_key, player['steam_id'])
            request = Request(player_url)
            response = urlopen(request)
            player_stat = json.loads(response.read())
            if 'gameid' in player_stat['response']['players'][0]:
                app_url = app_data % (int(player_stat['response']['players'][0]['gameid']))
                request = Request(app_url)
                response = urlopen(request)
                app = json.loads(response.read())
                if app[player_stat['response']['players'][0]['gameid']]['success']:
                    app_name = app[player_stat['response']['players'][0]['gameid']]['data']['name']
                    player_text = now_player % (player['name'], player['telegram_id'], app_name, int(player_stat['response']['players'][0]['gameid']))
                    text_response += player_text
                num_gamers += 1
    except KeyError, e:
        print('No players in file')

    if num_gamers == 0:
        text_response += '_nadie_'
    bot.send_message(chat_id=update.message.chat_id, text=text_response, parse_mode='Markdown')

dp = updater.dispatcher

que_handler = CommandHandler('alguien', alguien, filters=Filters.chat(enabled_chat))

dp.add_handler(que_handler)

# Start the Bot
updater.start_polling()

updater.idle()


if __name__ == '__main__':
    main()
