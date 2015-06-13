#!python3
import ast
import base64
from datetime import datetime
import json
import os
import hexchat

__module_name__ = "gossip.py"
__module_author__ = "Mika Wu"
__module_version__ = "0.2.1.150613"
__module_description__ = "Stores highlights/pms for future reading."

# Folder created in plugins directory to store mentions and config
LOGS_PATH = "hlogs/"

MENTION_STORE = 1
PM_STORE = 0

# Stores list of updated users/channels
CH_UPDATES = []
PM_UPDATES = []

def encode(channel):
	"""Encodes a channel name to urlsafe base64 to always obtain valid
	filesystem names. Must specify return as string due to differences
	between Python 2 and Python 3 string objets.
	"""
	return str(base64.urlsafe_b64encode(channel.encode("ascii")))


def date_conv(date_info):
	"""If passed a date string return datetime object for date;
	if passed a datetime object return a date string for it.

	Args:
		date: string format Y-m-d-H-M-S
	"""
	if isinstance(date_info, str):
		return datetime.strptime(date_info, "%Y-%m-%d-%H-%M-%S")
	else:
		return date_info.strftime("%Y-%m-%d-%H-%M-%S")


def store(channel, mention):
	"""Appends passed message to highlights text file, or creates
	it & adds if it doesn't exist. Creates log for each channel.
	"""
	global LOGS_PATH

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
	# Default assume no new mentions
	empty = True

	if older_than is None:
		# Set to NOW
		older_than = datetime.now()
	else:
		# Otherwise convert to datetime object
		older_than = date_conv(older_than)

	with open(LOGS_PATH + encode(channel), "a+") as highlights:
		highlights.seek(0)
		print("°===============°")
		with open(LOGS_PATH + "buffer", "w") as output:
			for line in highlights:
				mention_date = ast.literal_eval(line)
				# If the current line is more recent than the cutoff date,
				# we do something to it based on flag:
				# 	deletion: gets written to buffer file to be preserved
				#	ru: changes last tuple value from 0 to 1 for read
				if (date_conv(mention_date[0]) > older_than):
					output.write(line)
				else:
					if flag != "d":
						if ((flag == "ra") or 
							(flag != "ra" and mention_date[3] == 0)):
							# If something is going to be printed, it's not empty
							empty = False
							print(mention_date[2])
						if flag == "ru":
							mention_date[3] = 1
						output.write(str(mention_date) + "\n")
	
	# If empty still True means no mentions were printed
	if empty and flag != "d":
		print("No new mentions.")
	elif flag is "d":
		print("Log deleted.")
	print("°===============°")

	os.remove(LOGS_PATH + encode(channel))
	os.rename(LOGS_PATH + "buffer", LOGS_PATH + encode(channel))


def mention_cb(word, word_eol, userdata):
	"""Callback function to receive highlight events and PMs. Processes
	and passes appropriate arguments to storage.

	Args:
		word: Passed by hook. Contains user nick, message, and op status.
		word_eol: Passed by hook. Gives "word" contents from the provided
				  index and onward.
		userdata: Additional argument in hook can be passed through userdata.

	Returns:
		EAT_* constant: Controls how Hexchat procedes when callback returns.
		Here we will use "EAT_ALL" to soft "delete" the original message.

	See HEXCHAT documentation for futher information.
	"""
	global CH_UPDATES, PM_UPDATES
	if userdata == "hilight" and MENTION_STORE:
		channel = hexchat.get_info("channel")
		if channel not in CH_UPDATES:
			CH_UPDATES.append(channel)
			hexchat.set_pluginpref("gossip_ch_up", CH_UPDATES)
		store(channel, "<" + word[0] + "> " + word[1])
	elif userdata == "pm" and PM_STORE:
		user = word[0]
		if user not in PM_UPDATES:
			PM_UPDATES.append(user)
			hexchat.set_pluginpref("gossip_pm_up", PM_UPDATES)
		store(user, "<" + user + "> " + word[1])
	return hexchat.EAT_NONE


def usage():
	print("""Usage:
				/gossip new .. lists awaiting notifications (from X user, Y channel, etc.)
				/gossip read | r .. check new (unread) mentions
				/gossip readnoclear | rnc .. view new mentions; don't mark as read
				/gossip readall | ra .. view all stored mentions for current channel
				/gossip pms [r|ra|rnc|del] [user] .. read or delete pms stored from user
				/gossip delete | del .. deletes all mentions for the current channel
				/gossip toggle [mentions|pms|all] .. toggle storage of argument
				/gossip help | ? | --help .. see this message""")


def get_cb(word, word_eol, userdata):
	"""Callback function for gossip commands.

	Args:
		word: Passed by hook. Contains command, nick, and arguments.
		word_eol: Passed by hook. Gives "word" contents from the provided
				  index and onward (i.e., "command NICK arg", "NICK arg"...)
		userdata: Additional argument in hook can be passed through userdata.

	Returns:
		EAT_* constant: Controls how Hexchat procedes when callback returns.
		Here we will use "EAT_ALL" to soft "delete" the original message.

	See HEXCHAT documentation for futher information.
	"""
	global MENTION_STORE, PM_STORE, CH_UPDATES, PM_UPDATES

	for w in word:
		w = w.lower()

	if len(word) < 2:
		usage()
		return hexchat.EAT_HEXCHAT
	elif word[1] in ["reload", "rl"]:
		print("Restart HexChat to reload. Do *not* use /py reload.")
	elif word[1] in ["new"]:
		print("New mentions in channels: " + ", ".join(CH_UPDATES))
		print("New PMs from: " + ", ".join(PM_UPDATES))
	elif word[1] in ["read", "r"]:
		flag_mentions(hexchat.get_info("channel"), "ru")
		if hexchat.get_info("channel") in CH_UPDATES:
			CH_UPDATES.remove(hexchat.get_info("channel"))
	elif word[1] in ["readall", "ra"]:
		flag_mentions(hexchat.get_info("channel"), "ra")
		if hexchat.get_info("channel") in CH_UPDATES:
			CH_UPDATES.remove(hexchat.get_info("channel"))
	elif word[1] in ["readnoclear", "rnc"]:
		flag_mentions(hexchat.get_info("channel"), "r")
		if hexchat.get_info("channel") in CH_UPDATES:
			CH_UPDATES.remove(hexchat.get_info("channel"))
	elif word[1] in ["pms"]:
		if len(word) < 4:
			usage()
			return hexchat.EAT_HEXCHAT
		elif word[2] in ["read", "r"]:
			flag_mentions(word[3], "ru")
		elif word[2] in ["readall", "ra"]:
			flag_mentions(word[3], "ra")
		elif word[2] in ["readnoclear", "rnc"]:
			flag_mentions(word[3], "r")
		elif word[2] in ["delete", "del"]:
			flag_mentions(word[3], "d")
		# Something is being read, so we remove from awaiting notifications
		if word[3] in PM_UPDATES:
			PM_UPDATES.remove(word[3])
	elif word[1] in ["delete", "del"]:
		flag_mentions(hexchat.get_info("channel"), "d")
		if hexchat.get_info("channel") in CH_UPDATES:
			CH_UPDATES.remove(hexchat.get_info("channel"))
	elif word[1] in ["toggle"]:
		if len(word) < 3:
			usage()
			return hexchat.EAT_HEXCHAT
		if word[2] in ["mentions", "all"]:
			MENTION_STORE = 1 - MENTION_STORE
			hexchat.set_pluginpref("gossip_mentions", MENTION_STORE)
			print("Mention logging is now " + ("on" if MENTION_STORE else "off"))
		if word[2] in ["pms", "all"]:
			PM_STORE = 1 - PM_STORE
			hexchat.set_pluginpref("gossip_pms", PM_STORE)
			print("PM logging is now " + ("on" if PM_STORE else "off"))

	return hexchat.EAT_HEXCHAT


def main():
	global LOGS_PATH, MENTION_STORE, PM_STORE

	print(__module_name__, __module_version__, "has been loaded.")

	# Now "pull" from config
	MENTION_STORE = hexchat.get_pluginpref("gossip_mentions")
	PM_STORE = hexchat.get_pluginpref("gossip_pms")
	CH_UPDATES = hexchat.get_pluginpref("gossip_ch_up")
	PM_UPDATES = hexchat.get_pluginpref("gossip_pm_up")

	# If values are missing (first run), set defaults
	if MENTION_STORE is None:
		MENTION_STORE = 1
		hexchat.set_pluginpref("gossip_mentions", 1)
	if PM_STORE is None:
		PM_STORE = 0
		hexchat.set_pluginpref("gossip_pms", 0)
	if CH_UPDATES is None:
		CH_UPDATES = []
		hexchat.set_pluginpref("gossip_ch_up", [])
	if PM_UPDATES is None:
		PM_UPDATES = []
		hexchat.set_pluginpref("gossip_pm_up", [])

	hexchat.hook_command("gossip", get_cb)
	hexchat.hook_print("Channel Msg Hilight", mention_cb, "hilight")
	hexchat.hook_print("Private Message to Dialog", mention_cb, "pm")

if __name__ == "__main__":
	main()
