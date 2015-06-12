import hexchat

__module_name__ = "trimmer.py"
__module_author__ = "Mika Wu"
__module_version__ = "0.2.0.150606"
__module_description__ = "Trims nicknames to length."

# Set to truncation level in characters.
# Note that, if using a non-monospace font,
# not all nicks will be of the same length.
TRIM_TO = 11

# Optionally remove one extra character from the end of the nickname and
# replace it with the specified character to signify trimmed state.
# e.g., "DANtheBEASTman" --> on: "DANtheBEAS~"
#							off: "DANtheBEAST"
# Set to 1 to enable
# Set to 0 to disable
REPLACE_TRIM = 1
SIGN = "."

# Emitting same command as hook receives creates infinite loop.
# So, we must have a variable to signal to "stop" processing
# a particular event for a short time.
trimmed = False

def trim_cb(word, word_eol, userdata):
	"""Print user message with an abbreviated username
	if it exceeds the specified trim length.

	Args:
		word: Passed by hook. Contains user nick, message, and op status.
		word_eol: Passed by hook. Gives "word" contents from the provided
				  index and onward.
		userdata: Additional argument in hook can be passed through userdata.
				  Used here to better handle multiple types of message events.

	Returns:
		EAT_* constant: Controls how Hexchat procedes when callback returns.
		Here we will use "EAT_ALL" to soft "delete" the original message.

	See HEXCHAT documentation for futher information.
	"""
	global TRIM_TO, REPLACE_TRIM, SIGN, trimmed

	if trimmed:
		return

	nick = word[0]
	nick = hexchat.strip(nick, -1, 3)

	if len(nick) > TRIM_TO:
		# We're about to emit print so we set our signal variable to True.
		# When the emit triggers the hook, the function returns immediately.
		trimmed = True
		nick_trim = nick[0:TRIM_TO - REPLACE_TRIM] + REPLACE_TRIM * SIGN
		# print("emit_print({}, {}, {})".format(userdata, nick_trim, word[1]))
		hexchat.emit_print(userdata, nick_trim, word[1])
		# Now we set the signal back to False so we can process incoming events.
		trimmed = False
		return hexchat.EAT_ALL


# Script will check all messages and hilight messages with these two hooks.
# Refer to Settings/Text Events for additional event names.
hexchat.hook_print("Channel Message", trim_cb, "Channel Message")
hexchat.hook_print("Channel Msg Hilight", trim_cb, "Channel Msg Hilight")
# Hooks dialog windows w/ long nicks
hexchat.hook_print("Private Message to Dialog", trim_cb, "Private Message to Dialog")
#trim_cb(["attenuatedme","message", "@"], ["user","message", "@"], "Channel Message")
print(__module_name__, __module_version__, "has been loaded.")
