import discord
import feedparser
import asyncio
import datetime
from discord.ext import tasks

# Your bot's token
TOKEN = ''

# The Fresh RSS feed URL
RSS_URLS = ['https://cyberalerts.io/rss/latest-public',
           'https://securelist.com/feed/',
           'https://0dayfans.com/feed.rss',
           'https://feeds.feedburner.com/eset/blog',
           'https://news.sophos.com/en-us/category/threat-research/feed/',
           'https://feeds.feedburner.com/TheHackersNews?format=xml',
           'https://isc.sans.edu/rssfeed_full.xml',
           'https://podcast.darknetdiaries.com/',
           'https://krebsonsecurity.com/feed/',
           'https://www.cshub.com/rss/news',
           'https://www.cshub.com/rss/reports',
           'https://www.cshub.com/rss/categories/attacks',
           'https://www.exploitone.com/feed/',
           'http://feeds.feedburner.com/GoogleOnlineSecurityBlog']

# Set up intents
intents = discord.Intents.default()
intents.messages = True  # Enable the message content intent

# Set up Discord client
client = discord.Client(intents=intents)

# Function to fetch and send the latest news
def fetch_latest_news():
    news_items = []
    
    for rss_url in RSS_URLS:
        feed = feedparser.parse(rss_url)
    
        for entry in feed.entries[:5]:  # Get the latest 5 articles from each feed
            title = entry.title
            link = entry.link
            published = datetime.datetime(*entry.published_parsed[:6]).strftime("%Y-%m-%d %H:%M:%S")
            news_items.append(f"**{title}**\nPublished: {published}\n{link}\n")
    
    return "\n".join(news_items)

# Task to send the news to a channel every day
# @tasks.loop(hours=24)
async def send_daily_news():
    news = fetch_latest_news()
    
    # If the message exceeds 2000 characters, split it into chunks
    max_length = 1500  # Discord's message limit is 2000 characters
    while len(news) > max_length:
        # Find the last space or newline character to split the message properly
        split_point = news.rfind(' ', 0, max_length)
        if split_point == -1:
            split_point = max_length  # Fallback if no space is found

        chunk = news[:split_point]
        await send_chunk(chunk)
        news = news[split_point:].lstrip()  # Remove leading spaces/newlines for the next chunk

    # Send the remaining part if any
    if news:
        await send_chunk(news)

async def send_chunk(chunk):
    # Replace with your channel ID
    channel = client.get_channel()
    try:
        await channel.send(f"**Latest Cybersecurity News**:\n{chunk}")
    except discord.errors.HTTPException as e:
        print(f"Error sending message: {e}")

# On bot ready, start the daily news task
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    await send_daily_news()
    await client.close()

# Run the bot
client.run(TOKEN)
