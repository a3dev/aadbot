def link(text, link):
	badChars = ['\n', '\r']
	for char in badChars:
		text = text.replace(char, '')

	text = text.strip()
	return "[" + text + "](" + link + ")"

def title(text):
    return "#" + text

def quote(text):
    return ">" + text

def safe(text):
	#remove "code" markup
	text = text.replace('   ', '')
	#remove "`" code snippet
	text = text.replace('`', '\'')
	#escape #
	text = text.replace('#', '\#')
	return text

def bold(text):
    return '**' + text.strip() + '**'

def italics(text):
    return '*' + text.strip() + '*'

def strikethrough(text):
    return '~~' + text + '~~'

def superscript(text):
	return '^' + ' ^'.join(text.split())

def lineNumber(text):
	return '1. ' + text + '\n'

def codeSnippet(text):
	return '`' + text + '`'


newline = '\n\n'

hline = newline + newline + '______' + newline + newline
