import hexchat

__module_name__ = "trimmer"
__module_author__ = "Mika Wu"
__module_description__ = """Trims nicknames. Worst enemy of
							aaaaaaaaaaaaaaaaaaaaaaa, DANtheBEASTman, et al."""

# Set to truncation level in characters.
# Note that, if using a non-monospace font,
# not all nicks will be of the same length.
TRIM = 11

# Optionally remove one extra character from the end of the nickname and
# replace it with the specified character to signify trimmed state.
# e.g., "DANtheBEASTman" --> on: "DANtheBEAS~"
#							off: "DANtheBEAST"
# Set to 1 to enable
# Set to 0 to disable
REPLACE_TRIM = 1
SIGN = "~"


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
		Here we will use "EAT_HEXCHAT" to soft "delete" the original message.

	See HEXCHAT documentation for futher information.
	"""

	nick = word[0]

	if len(nick) > TRIM:
		nick_trim = nick[0:TRIM - REPLACE_TRIM] + REPLACE_TIME * SIGN
		hexchat.emit_print(userdata, nick_trim, word[1])
		return hexchat.EAT_HEXCHAT


# Script will check all messages and hilight messages with these two hooks.
# Refer to Settings/Text Events for additional event names.
hexchat.hook_print("Channel Message", trim_cb, "Channel Message")
hexchat.hook_print("Channel Msg Hilight", trim_cb, "Channel Msg Hilight")
