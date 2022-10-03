from pydoc import cli
import threading
from unicodedata import name
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from http import client
from json import load
import os
from re import L
from time import process_time_ns
import discord
from dotenv import load_dotenv
from gettext import find
import json
from turtle import xcor
from numpy import place
from pandas import NA
from unicodedata import name
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import schedule
from multiprocessing import Process
import asyncio
import keyboard
from discord_webhook import DiscordWebhook, DiscordEmbed

dotenv_path = os.path.join(os.path.dirname(__file__), 'secrets.env')
load_dotenv(dotenv_path)

TOKEN = os.environ["DISCORD_TOKEN"]
intents = discord.Intents.default()
intents.message_content = True
FILE_PATH = ".\\players.json"
players = []
client = discord.Client(intents=intents)
WEEBHOOK_URL = os.environ.get("WEBHOOK_URL")


def read_file():
    with open(FILE_PATH, 'r') as f:
        players = json.load(f)
    f.close()
    return players

def add_player(name, rating, revision, URL, PR):
    print(players)
    #write to the players.json file
    with open(FILE_PATH, 'w') as f:
        players.append({"name": name, "revision": revision, "Rating": rating, "URL": URL, "PR" : PR})
        json.dump(players, f, indent=4)
    f.close()

def finding_player(URL):
    # check if the player is in the file
    for player in players:
        if player["URL"] == URL:
            print("Player already in the file")
            return

    options = FirefoxOptions()
    options.add_argument('--headless' )
    driver = webdriver.Firefox(options=options)
    driver.get(URL)
    
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # try to get the name of the player if it fails then the player is not on futbin and return
    try:
        name = soup.find("div", {"class": "pcdisplay-name"}).text
    except:
        print("Player not found")
        return
    try:
        pr = soup.find("div", {"id": "pr_pc"}).text
        # replace PR: in the string
        pr = pr.replace("PR: ", "")
    except:
        print("Player not found")
        return
    rating = soup.find("div", {"class": "pcdisplay-rat"}).text

    # find the revision of the player in the table called table table-info
    revision = soup.find("table", {"class": "table table-info"}).text
    # in revison find revison till 
    revision = revision[revision.find("Revision"):revision.find("Att. WR")]

    #remove the word Revision
    revision = revision.replace("Revision", "")
    # remove all the white space
    revision = revision.replace(" ", "")
    #remove all the new lines from the string
    revision = revision.replace("\n", "")

    add_player(name, rating, revision, URL, pr)
    driver.quit()

# remove the player from players and write the new list to the file
def remove_player(URL):
    for player in players:
        if player["URL"] == URL:
            players.remove(player)
    with open(FILE_PATH, 'w') as f:
        json.dump(players, f, indent=4)
    f.close()

async def get_price():
    # send in general that the bot is getting the price
    players = read_file()
    players_urls = []
    for x in players:
       # print(x["URL"])
        players_urls.append(x['URL'])

    for URL in players_urls:
        options = FirefoxOptions()
        options.add_argument('--headless' )
        driver = webdriver.Firefox(options=options)
        print("Getting price for: ", URL)
        driver.get(URL)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        try:
            price = soup.find("div", {"id": "pr_pc"}).text
            # remove PR: from the string
            price = price.replace("PR: ", "")
            last_sold = soup.find("span", {"id": "pc-lowest-1"}).text
        except:
            print("Player not found")
            return
        # check to see if the current pr is the same as the one on the players
        for player in players:
            if player["URL"] == URL:
                if player["PR"] != price:
                    # send a message to the channel that the price has changed
                    print("Price changed")
                    send_message("Price changed for: " + player["name"] + " old price: " + player["PR"] + " new price: " + price + " last sold: " + last_sold)
                    player["PR"] = price
                    with open(FILE_PATH, 'w') as f:
                        json.dump(players, f, indent=4)
                    f.close()
        print(price, "last sold:" , last_sold)
        driver.quit()
    print("Done getting price")


def send_message(message):
    webhook = DiscordWebhook(WEEBHOOK_URL,username="PlayerPriceChecker", content=message)
    response = webhook.execute()
    print(response)

@client.event
async def on_connect():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):

    if message.content.startswith('$all'):
        print(f'{message.author} has requested all players')
        print("players: ", players)
        read_file()
        for player in players:
            print("Player Details: " , player)
            await message.channel.send(f'Name: {player["name"]}\nRating: {player["Rating"]}\nRevision: {player["revision"]}\nURL: {player["URL"]}')

    if message.content.startswith('$add '):
        # check to see if its of an correct URL format
        if message.content[5:].startswith("https://www.futbin.com/23/player/"):
            URL = message.content[5:]
            await message.channel.send(f'Added {URL} to the file')
            print(f"Added {URL} to the file")
            finding_player(URL)
        else:
            await message.channel.send(f'Incorrect URL format')

    if message.content.startswith('$delete '):
        # get the number from the message and remove the same amount of messages from the channel
        number = int(message.content[8:])
        if number == -1:
            await message.channel.purge()
        await message.channel.purge(limit=number)

    if message.content.startswith('$remove '):
        if message.content[8:].startswith("https://www.futbin.com/23/player/"):
            URL = message.content[8:]
            await message.channel.send(f'removing {URL} from the file')
            print(f"removing {URL} from the file")
            remove_player(URL)
        else:
            await message.channel.send(f'Incorrect URL format')
    if message.content.startswith('$test'):
        chan = client.get_all_channels()
        for channel in chan:
            print(channel)
    if message.content.startswith('$price'):
        await get_price()

def client_run():
    client.run(TOKEN)

def get_price_hourly():
    while True:
        asyncio.run(get_price())
        time.sleep(3600)


if __name__ == "__main__":
    players = read_file()
    # # run both client and get_price_hourly at the same time
    t1 = threading.Thread(target=client_run)
    t1.daemon = True
    t2 = threading.Thread(target=get_price_hourly)
    t2.daemon = True
    t2.start()
    t1.start()
    t2.join()
    t1.join()