#!/usr/bin/env python3
import logging
import feedparser
import json
import os
import sys
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
BOT_CHANNEL = os.environ["BOT_CHANNEL"]

CACHE_FILE = "cache.json" # file used to store links between runs
DEBUG_PORT = 8080

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

		self.key = self.link # here if key need to be changed
	
	def format(self):
		'''
		Returns final Slack message
		'''
		# Slack uses unusual markdown for links (<link|name>)
		return f"<{self.link}|{self.title}> written by _{self.author}_ [{self.published}]\n" + f"\n> {self.summary}" 

def read_cache():
	'''
	Reads previously stored links from the CACHE file
	'''
	try:
		with open(CACHE_FILE, 'r') as cache:
			cache_data = json.loads(cache.read())["links"]
			logging.debug(f"CACHE READ {cache_data}")
			return set(cache_data)

	except FileExistsError:
		with open(CACHE_FILE, 'w') as cache:
			logging.debug("CACHE CREATED")
			cache.write(json.loads({"links" : []}))
		return {}

	except:
		return {}
		
def write_to_cache(links):
	''''
	Stores the blog links from the website in the CACHE_FILE
	'''
	with open(CACHE_FILE, 'w') as cache:
		dict_links = {"links" : list(links)}
		cache.write(json.dumps(dict_links))

if __name__ == "__main__":
	print("---RUNNNING---")

	# --args--
	args = sys.argv
	if len(args) >= 2 and args[1] == "--release":
		logging.basicConfig(level=logging.INFO)
		URL = os.environ["URL"]
	else:
		logging.basicConfig(level=logging.DEBUG) # debug by default so debuggers can be used without args
		URL = f"http://localhost:{DEBUG_PORT}"

	# --slack--
	slack_client = WebClient(SLACK_BOT_TOKEN)
	logging.debug("AUTHORISED SLACK CLIENT")

	#--read cache--
	stored_posts = read_cache()

	#--retrieving rss files--
	check = feedparser.parse(URL)
	if check.bozo: # test for invalid responses
		logging.error(f"INVALID URL {URL}")

	update = {post.key : post for post in [Post(entry) for entry in check.entries]}
	new = set(update.keys()).difference(stored_posts)

	for key in new:
		post = update[key]
		logging.debug(f"PROCESSING {post.title}")
		send_to_slack(slack_client,post.format())
	
	write_to_cache(update.keys()) #storing keys in cache for next read
	