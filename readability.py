from pprint import pprint
import pickle
from bs4 import BeautifulSoup
import json

import requests

import redditText

REDABILITY_RQ_MIN_LEN = 500

def processShortURL(URL):
    shortURL = ['t.co', 'lnkd.in', 'db.tt', 'qr.ae', 'goo.gl', 'tinyurl.com', 'bit.ly', 'bitly.com', 'cur.lv', 'ow.ly', 'is.gd', 'twitthis.com', 'j.mp', 'qr.net', 'v.gd']
    badShortURL = ['adf.ly', 'cur.lv', 'ity.im', 'q.gs', 'buzurl.com', 'u.bb', 'prettylinkpro.com', 'vzturl.com', 'tr.im']

    emptyLink = '#'
    if any(item in URL for item in badShortURL):
        return emptyLink
    elif any(item in URL for item in shortURL):
        r = requests.get(URL)
        if r.status_code == requests.codes.ok:
            return r.url
        else:
            return emptyLink
    return URL

def getReadabilityText(url):
    print("[0][readability][get text]")
    resJSON = ''

    API_BASE_URL_PARSER = 'https://readability.com/api/content/v1/parser'

    token='86a8292ab866f478a6103440f94413d3f221f3c7'

    req = API_BASE_URL_PARSER + '?url=' + url + '&token=' + token

    r = requests.get(req)

    if r.status_code is 200:
        resJSON = r.json()
        pprint(resJSON)
        print("[1][readability][get text][len : ", len(resJSON), "]")
        return resJSON
    else:
        print("[1][readability][get text][ERROR]")
        return None

def getBodyText(tag):

    body_text = ''

    for j in tag.descendants:
        try:
            tagName = j.name
            #{'strong', 'a', 'br', None, 'em'}
            if(tagName == None):
                body_text += j.string
            elif(tagName == 'br'):
                body_text += "\n"
            elif(tagName == 'p'):
                body_text += j.string + '\n\n'
                j.clear()
            elif(tagName == 'a'):
                print("getting links")
                body_text += '[' + processShortURL(j.string) + ']' + '(' + processShortURL(j['href']) + ')'
                j.clear()
            elif(tagName == 'blockquote'):
                print("blockquote")
                body_text += '>' +  getBodyText(j) + '\n\n\n'
                j.clear()
        except Exception as e:
            print("Error in getBodyText(): ", e)

    return body_text

def getArticleText(soup):
	print("[0][BeautifulSoup][parse, extract main text]")

	for i in soup.descendants:
		if(i.name == "div"):
			try:
				for attribute in i['class']:
					attribute = attribute.lower()
					if attribute == 'normal':
						return getBodyText(i)
					elif attribute == 'content':
						return getBodyText(i)
					elif attribute == 'ins_storybody':
						return getBodyText(i)
					elif attribute == 'highlights-chunk':
						i.clear()
						return getBodyText(i.parent)
					else:
						return getBodyText(soup)
			except Exception as e:
				print("Error in getArticleText(): ", e)

	print("[-1][BeautifulSoup][ERROR][len : ", len(body_text), "]")
	return None

def getArticle(url):
	articleDict = {}

	#try readability
	resJSON = getReadabilityText(url)

	#get the main text
	content = resJSON['content']
	soup = BeautifulSoup(content, 'html.parser')
	articleText = getArticleText(soup)
	redditSafeArticleText = redditText.safe(articleText)

	if len(redditSafeArticleText) < REDABILITY_RQ_MIN_LEN:
		return None

	articleDict['text'] = redditSafeArticleText

	articleDict['title'] = redditText.title(resJSON['title'])

	lead_image_url = resJSON['lead_image_url']
	excerpt = resJSON['excerpt']
	if excerpt is not '' and lead_image_url is not None and lead_image_url is not '':
		articleDict['subtext'] = redditText.link(excerpt, lead_image_url)
	elif lead_image_url is not None and lead_image_url is not '':
		articleDict['subtext'] = redditText.link('IMAGE', lead_image_url)
	elif excerpt is not '':
		articleDict['subtext'] = excerpt

	articleDict['images'] = None

	Readability_Credit = redditText.superscript("Powered by") + " " + redditText.link(redditText.superscript("Readability"), "https://www.readability.com")
	articleDict['credit'] = Readability_Credit

	return articleDict
