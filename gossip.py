#!python3
import ast
from datetime import datetime, timedelta
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

def date_conv(date):
	"""If passed a date string return datetime object for date;
	if passed a datetime object return a date string for it.

	Args:
		date: string format Y-m-d-H-M-S
	"""
	if type(date) == str:
		return datetime.strptime(date, "%Y-%m-%d-%H-%M-%S")
	else:
		return date.strftime("%Y-%m-%d-%H-%M-%S")

def store(channel, mention):
	"""Appends passed message to highlights text file, or creates
	it & adds if it doesn't exist. Creates log for each channel.
	"""
	global LOGS_PATH

	if not os.path.exists("hlogs"):
		os.makedirs("hlogs")
	with open(LOGS_PATH + encode(channel), "a") as highlights:
		store = [date_conv(datetime.now()), channel, mention, 0]
		highlights.write(str(store) + "\n")


def flag_mentions(channel, flag, older_than = None):
	"""Flag some/all stored mentions for a channel by date.

	Args:
		flag: For deletion (d), read (r), read and update (ru), read-all (ra)
				d: deletes messages
				r: print out all messages marked as unread
				ru: print out unread messages and mark as read
				ra: print out all messages, regardless of read/unread status

		older_than: Only affect messages from before this cutoff date.
					e.g.
						only delete messages older than YY/MM/DD
						only mark messages older than YY/MM/DD as read
					If not given, uses the current datetime (affects all).

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
		# Set to NOW
		older_than = datetime.now()
	else:
		# Otherwise convert to datetime object
		older_than = date_conv(older_than)

	with open(LOGS_PATH + encode(channel), "r") as highlights:
		with open(LOGS_PATH + "buffer", "w") as output:
			for line in highlights:
				mention_date = ast.literal_eval(line)
				# If the current line is more recent than the cutoff date,
				# we do something to it based on flag:
				# 	deletion: gets written to buffer file to be preserved
				#	ru: changes last tuple value from 0 to 1 for read
				if (date_conv(mention_date[0]) < older_than):
					if flag != "d":
						if ((flag == "ra") or 
							(flag != "ra" and mention_date[3] == 0)):
							print(mention_date[2])
						if flag == "ru":
							mention_date[3] = 1
						output.write(str(mention_date) + "\n")
				else:
					output.write(line)

	os.remove(LOGS_PATH + encode(channel))
	os.rename(LOGS_PATH + "buffer", LOGS_PATH + encode(channel))
