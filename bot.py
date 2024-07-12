import logging
import feedparser
import json
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
BOT_CHANNEL = os.environ["BOT_CHANNEL"]
URL = os.environ["URL"]
CACHE_FILE = "cache.json"

logging.basicConfig(level=logging.INFO)

def send_to_slack(slack_client, msg):
	try: 
		slack_client.chat_postMessage(
		channel = BOT_CHANNEL, 
		text = msg
	)
	except SlackApiError as e:
		logging.error(f"Request to Slack API Failed: {e.response.status_code}.")
		logging.error(e.response)

class Post:
	def __init__(self, entry):
		self.title = entry["title"]
		self.author = entry["author"]
		self.published = entry["published"]
		self.summary = entry["summary"]
		self.link = entry["link"]

		self.key = self.link #here if key need to be changed
	
	def format(self):
		return f"<{self.link}|{self.title}> written by _{self.author}_ [{self.published}]\n" + f"\n> {self.summary}"

def read_cache():
	try:
		with open(CACHE_FILE, 'r') as cache:
			return set(json.loads(cache.read())["links"])
	except FileExistsError:
		with open(CACHE_FILE, 'w') as cache:
			cache.write(json.loads({"links" : []}))
	
	finally:
		return []
		
def write_to_cache(links):
	with open(CACHE_FILE, 'w') as cache:
		dict_links = {"links" : list(links)}
		cache.write(json.dumps(dict_links))

if __name__ == "__main__":
	print("---RUNNNING---")
	slack_client = WebClient(SLACK_BOT_TOKEN)
	logging.debug("AUTHORISED SLACK CLIENT")

	stored_posts = read_cache()
	logging.debug("CACHE READ")

	check = feedparser.parse(URL)
	update = {post.key : post for post in [Post(entry) for entry in check.entries]}

	new = set(update.keys()).difference(stored_posts)

	for key in new:
		post = update[key]
		logging.debug(f"PROCESSING {post.title}")
		send_to_slack(slack_client,post.format())
	
	write_to_cache(update.keys())
	