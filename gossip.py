#!python3
import ast
from datetime import datetime
import os
import base64
#import hexchat

__module_name__ = "gossip.py"
__module_author__ = "Mika Wu"
__module_version__ = "0.1.0.150611"
__module_description__ = "Stores highlights in a file for future reading."

LOGS_PATH = "hlogs/"


def encode(channel):
	"""Encodes a channel name to urlsafe base64 to always obtain valid
	filesystem names. Must specify return as string due to differences
	between Python 2 and Python 3 string objets.
	"""
	return str(base64.urlsafe_b64encode(channel.encode("ascii")))


def store(channel, mention):
	"""Appends passed message to highlights text file, or creates
	it & adds if it doesn't exist. Creates log for each channel.
	"""
	global LOGS_PATH

	if not os.path.exists("hlogs"):
		os.makedirs("hlogs")
	with open(LOGS_PATH + encode(channel) + ".txt", "a") as highlights:
		store = (datetime.now().strftime("%Y-%m-%d"),
				 datetime.now().strftime("%H:%M"), channel, mention)
		highlights.write(str(store) + "\n")


def get_mentions(channel, since = "unread"):
	"""Print some/all stored mentions for a channel by date."""
	global LOGS_PATH

	with open(LOGS_PATH + encode(channel) + ".txt", "r") as highlights:
		for line in highlights:
			print(line, end="")


def flag_mentions(channel, flag, older_than = None):
	"""Flag some/all stored mentions for a channel by date.

	Args:
		flag: For deletion or read/unread.
		older_than: Flags all messages from before this cutoff date given
					in ISO format (YYYY-MM-DD). If not specified, flags all
					messages from before the current date.

	As a side note, while I don't expect the number of lines to exceed a
	couple hundred, reading line-by-line and writing to a separate file
	instead of doing a double pass (read all lines, close file, reopen file
	to overwrite, and then re-writing specific lines) is much less RAM
	intensive. With files in the tens/hundreds of gb+ you will probably run
	out of memory with a double-pass, whereas a single-pass and replace should
	be fine. So we'll use that here :)
	"""
	global LOGS_PATH

	if older_than == None:
		older_than = datetime.now().strftime("%Y-%m-%d")

	with open(LOGS_PATH + encode(channel) + ".txt", "r") as highlights:
		with open(LOGS_PATH + "buffer.txt", "w") as output:
			for line in highlights:
				mention_date = ast.literal_eval(line)
				# If the current line is from our cutoff date or newer
				# then we write it to our new file
				if (datetime.strptime(mention_date[0], "%Y-%m-%d") >=
					datetime.strptime(older_than, "%Y-%m-%d")):
					output.write(line)

	os.remove(LOGS_PATH + encode(channel) + ".txt")
	os.rename(LOGS_PATH + "buffer.txt", LOGS_PATH + encode(channel) + ".txt")
