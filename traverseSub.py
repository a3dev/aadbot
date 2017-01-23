#source : https://github.com/reddit/reddit/wiki/OAuth2-Quick-Start-Example

import json
import time
import re
import pickle
from pprint import pprint

import requests
import requests.auth

import extractText
import redditText

#make the log file look pretty

print()
print()
print()
print("#######################################################################")
print("#######################################################################")
print(":::::::::::::::::::::::::::::LOG FILE START::::::::::::::::::::::::::::")
print (time.ctime())
print(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
print()
print()
print()
print()


#reddit quirks
MAX_COMMENT_LENGTH = 9500

def prepareComment(thing_id, cDict):
	pprint(cDict)
	newline = '\n'
	hline = newline + newline + '___' + newline + newline

	#noc ~ number of comments :D
	noc = len(cDict['text'])

	if noc > 1:
		for index in cDict['text']:
			if index == 0:
				if cDict['title'] is not None:
					ctext = cDict['title'] + hline
				if cDict['subtext'] is not None:
					ctext += cDict['subtext'] + hline
				ctext += cDict['text'][index]

				res = postComment(thing_id, ctext)

				#the response for posting a comment is garbled with jquery and json
				#using JSON
				pattern = '"link_id": "\w{9}"'
				prog = re.compile(pattern)
				result = prog.match(res)
				link_id_str = result.group()

				t1 = link_id_str.split(":")[1]
				t2 = t1.replace('"', '')
				link_id = t2.replace(' ', '')
				thing_id = link_id

			elif index == noc - 1:
				ctext = cDict['text'][index]
				ctext += hline + cDict['botText']
				ctext += hline + cDict['credit']

				res = postComment(thing_id, ctext)
			else:
				ctext = cDict['text'][index]
				res = postComment(thing_id, ctext)

				#the response for posting a comment is garbled with jquery and json
				#using JSON
				pattern = '"link_id": "\w{9}"'
				prog = re.compile(pattern)
				result = prog.match(res)
				link_id_str = result.group()

				t1 = link_id_str.split(":")[1]
				t2 = t1.replace('"', '')
				link_id = t2.replace(' ', '')
				thing_id = link_id
	else:
		if cDict['title'] is not None:
			ctext = cDict['title'] + hline
		if cDict['subtext'] is not None:
			ctext += cDict['subtext'] + hline
		if cDict['images'] is not None:
			ctext += cDict['images'] + hline
		ctext += cDict['text'][0]
		ctext += hline + cDict['botText']
		ctext += hline + cDict['credit']

		res = postComment(thing_id, ctext)

def postComment(thing_id, text):
	print("[0][reddit][post comment]")
	redditOAUTH = 'https://oauth.reddit.com'
	apiReq = '/api/comment'

	data_post = {
		"text": text,
		"parent": thing_id
	}

	r = requests.post(redditOAUTH + apiReq, data=data_post, headers = getHeaders())

	if r.status_code is not 200:
		print("[1][reddit][post comment][Error][status code (default 200): ", r.status_code, "]")

	res = r.json()

	print("[1][reddit][post comment][status code (default 200): ", r.status_code, "]")

	return res

def deleteThing(thing_id):
	print("[0][reddit][delete thing]")
	redditOAUTH = 'https://oauth.reddit.com'
	apiReq = '/api/del'

	data_post = {
		"id": thing_id
	}

	r = requests.post(redditOAUTH + apiReq, data=data_post, headers = getHeaders())

	if r.status_code is not 200:
		print("[1][reddit][delete thing][Error][status code (default 200): ", r.status_code, "]")

	resJSON = r.json()

	print("thing deleted : ", thing_id)

	print("[1][reddit][delete thing][status code (default 200): ", r.status_code, "]")

	print("thing delete", r.text, r.url)

	return resJSON

def getProcessedLinks(username):
	print("[0][reddit][get list of processed links]")

	processedLinks = []

	try:
		processedLinks = pickle.load(open("processedLinks.p", "rb" ))
	except Exception as e:
		print("Cannot load 'processedLinks.p' from disk. Error : ", e)

		print("Getting processed links from bot history.")
		redditOAUTH = 'https://oauth.reddit.com'
		apiReq = '/user/' + username + '/comments'

		payload = {
			"show": "given",
			"sort": "new",
			"t": "day",
			"username": username,
			"count": 0,
			"limit": 100
		}

		r = requests.get(redditOAUTH + apiReq, params = payload, headers = getHeaders())

		if r.status_code is not 200:
			print("[1][reddit][get list of processed links][status_code : ", r.status_code, "]")
			return None

		resJSON = r.json()

		try:
			comments = resJSON['data']['children']
			for comment in comments:
				processedLinks.append(comment['data']['link_id'])
		except Exception as e:
			print("[1][reddit][get list of processed links][Error : ", e, "]")
			return None

	uniqueProcessedLinks = list(set(processedLinks))
	print("processedLinks retrieved : ", len(uniqueProcessedLinks))
	print("[1][reddit][get list of processed links]")
	return uniqueProcessedLinks

def setProcessedLinks(processedLinks):
	try:
		pickle.dump(processedLinks, open("processedLinks.p", "wb"))
	except Exception as e:
		print("cannot save 'processedLinks.p' to disk : ", e)
		return False
	else:
		return True

def getPostInfo(thing_id):
	time.sleep(1)
	print("[0][reddit][get post info]")

	if 't3_' not in thing_id:
		thing_id = 't3_' + thing_id

	postInfo = {}

	redditOAUTH = 'https://oauth.reddit.com'
	apiReq = '/by_id/' + thing_id

	r = requests.get(redditOAUTH + apiReq, headers = getHeaders())

	if r.status_code is not 200:
		print("[1][reddit][get unread messages][status_code : ", r.status_code, "]")
		return None

	resJSON = r.json()
	postInfo = resJSON['data']['children']

	print("[1][reddit][get post info]")
	return postInfo

def getSubMods(subreddit):
	time.sleep(1)
	print("[0][reddit][get sub mods]")

	subMods = []

	redditOAUTH = 'https://oauth.reddit.com'
	apiReq = '/r/' + subreddit + '/about/moderators'

	r = requests.get(redditOAUTH + apiReq, headers = getHeaders())

	if r.status_code is not 200:
		print("[1][reddit][get sub mods][status_code : ", r.status_code, "]")
		return None

	resJSON = r.json()

	for item in resJSON['data']['children']:
		subMods.append(item['name'])

	return subMods

def getProcessedMessages():
	processedMessages = {}

	try:
		processedMessages = pickle.load(open("processedMessages.p", "rb"))
	except Exception as e:
		print("cannot load 'processedMessages.p' from disk : ", e)

	return processedMessages

def setProcessedMessages(processedMessages):
	try:
		pickle.dump(processedMessages, open("processedMessages.p", "wb"))
	except Exception as e:
		print("cannot save 'processedMessages.p' to disk : ", e)
		return False
	else:
		return True

def dictDifference(dict1, dict2):
	#removes any elements of dict2 from dict1

	diff = dict1.copy()

	for i in dict1:
		for j in dict2:
			if dict1[i] == dict2[j]:
				del diff[i]
				break
	return diff


def setDomains(action, domainList=[]):
	domains=getDomains()

	if action == "list":
		return domains
	elif action == "add":
		for domain in domainList:
			if domain not in domains:
				if '.' in domain:
					domains.append(domain)
	elif action == "remove":
		for domain in domains:
			if domain in domainList:
				domains.remove(domain)
	else:
		return

	pickle.dump(domains, open("domains.p", "wb" ))
	return domains

def configDomains(replyThing, command, comment_author, post_subreddit):
	#add, remove, list domains
	if '-list' in command or '-l' in command:
		res = setDomains("list")
		comment = 'domains : '
		for item in res:
			comment += item + ' | '

		print(comment)
		postComment(replyThing, comment)
	elif ' -add ' in command or ' -a ' in command:
		MOD = isMOD(comment_author, post_subreddit)

		if not MOD:
			return

		if ' -add ' in command:
			dlist = command.split('-add')[-1]
		else:
			dlist = command.split('-a')[-1]

		dlist = ''.join(dlist.split())
		dlist = dlist.split(',')

		res = setDomains("add", dlist)

		comment = 'domains : '
		for item in res:
			if item in dlist:
				comment += redditText.bold(item) + ' | '
			else:
				comment += item + ' | '

		print(comment)
		postComment(replyThing, comment)
	elif ' -remove ' in command or ' -r ' in command:
		MOD = isMOD(comment_author, post_subreddit)

		if not MOD:
			return

		if ' -remove ' in command:
			dlist = command.split('-remove')[-1]
		else:
			dlist = command.split('-r')[-1]
		dlist = ''.join(dlist.split())
		dlist = dlist.split(',')

		res = setDomains("remove", dlist)


		comment = 'domains : '
		for item in res:
			comment += item + ' | '
		for item in dlist:
			comment += redditText.strikethrough(item) + ' | '


		print(comment)
		postComment(replyThing, comment)

def isOP(comment_author, post_thingName):
	#check if user is OP
	#get the post author name
	postInfo = getPostInfo(post_thingName)
	post_author = postInfo[0]['data']['author']
	if comment_author == post_author:
		return True

	return False

def isMOD(comment_author, post_subreddit):
	#check if the user is a MOD
	#get the mods of the sub
	subMods = getSubMods(post_subreddit)
	if comment_author in subMods:
		return True

	return False

def processCommands(msgDict):
	print("[0][reddit][process commands]")
	if msgDict is None:
		print("[1][reddit][process commands][no new messages]")
		exit()

	for index in msgDict:
		message = msgDict[index]
		msg = message['msg']
		msg_thingName = message['msg_thingName']
		parent_thingName = message['parent_thingName']
		post_thingName = message['post_thingName']
		comment_author = message['comment_author']
		post_subreddit = message['post_subreddit']

		msg_lower_case = msg.lower()

		#delete the main comment if the OP wishes so
		if msg_lower_case == 'delete' or msg_lower_case == 'remove':
			OP = isOP(comment_author, post_thingName)
			if not OP:
				break
			deleteThing(parent_thingName)
		elif 'domains' in msg_lower_case:
			configDomains(msg_thingName, msg_lower_case, comment_author, post_subreddit)


	#save the processed messages to avoid repetitions
	processedMessages = getProcessedMessages()
	for i in msgDict:
		pass
		processedMessages[len(processedMessages.keys())] = msgDict[i]

	setProcessedMessages(processedMessages)

	print("[1][reddit][process commands]")

##########MAIN###########
def getDomains():
	#bot will work on these websites
	domains = []
	try:
		domains = pickle.load(open("domains.p", "rb"))
	except Exception as e:
		domains = [
			"timesofindia.indiatimes.com",
			"ndtv.com",
			"indiatoday.intoday.in",
			"economictimes.indiatimes.com"
		]
		print("config domains, error : ", e)

	return domains

def relevantDomain(url):
	domains = getDomains()
	blacklist = ['ndtv.com/video', '/liveblog/', 'sports.ndtv']

	if url in blacklist:
		return False

	for domain in domains:
		if domain in url:
			return True

	return False

time.sleep(1)
messages = getMessages()
time.sleep(1)
processCommands(messages)


time.sleep(1)
newPosts = getNewPosts(SUBREDDIT)
if newPosts is None:
	print("FATAL ERROR : cannot get new posts")
	exit()

time.sleep(1)
processedLinks = getProcessedLinks(USER)

print("last 20 processed links : ")
try:
	print(processedLinks[-20:])
except Exception as e:
	print("cannot print processed links : ", e)


if processedLinks is None:
	print("FATAL ERROR: cannot get processed links")
	exit()

processPosts(newPosts)
