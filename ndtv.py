import requests
from pprint import pprint
import pickle
from bs4 import BeautifulSoup
import json
import redditText

#constants
MIN_IMAGE_SIZE = 9000 #bytes

def getTagWithAttrValue(soup, tagName, attr, value):
	for element in soup.descendants:
		try:
			if element.name == tagName:
				if element.has_attr(attr):
					values =  element.attrs[attr]
					if type(values) is list:
						for item in values:
							if value == item.lower():
								return element
					else:
						if values == value:
							return element
		except Exception as e:
			print(e)

	return None

def getImagesOfSize(imageList, length):
	images = []
	for image in imageList:
		r = requests.get(image, stream=True)
		if int(r.headers['Content-Length']) > length:
			images.append(image)

	return images

def resolveShortURL(URL):
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


def getArticle(url):
	print("[0][NDTV EXTRACTOR]")

	print("url : ", url)

	headers = {
		'user-agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'
	}


	r = requests.get(url, headers=headers)

	'''
	try:
		pickle.dump(r, open("page.p", "wb" ))
	except Exception as e:
		pass

	try:
		r = pickle.load(open("page.p", "rb"))
	except Exception as e:
		pass
	'''

	soup = BeautifulSoup(r.text, 'html.parser')

	#get title
	print("[0][GET TITLE]")

	title = None

	titleTag = getTagWithAttrValue(soup, 'h1', 'itemprop', 'headline')

	if titleTag is None or titleTag.string == '':
		titleTag = getTagWithAttrValue(soup, 'div', 'itemprop', 'headline')

		if titleTag is not None:
			title = titleTag.get_text()
		else:
			print("[-1][GET TITLE][ERROR][not found]")
	else:
		title = redditText.bold(titleTag.string)

	print("[1][GET TITLE]")
	print(title)

	#get main article node
	print("[0][GET MAIN NODE OF THE ARTICLE]")
	mainArticleTag = getTagWithAttrValue(soup, 'div', 'itemprop', 'articleBody')

	if mainArticleTag is None:
		print("[-1][GET MAIN NODE OF THE ARTICLE][ERROR]")

	print("[1][GET MAIN NODE OF THE ARTICLE]")
	#get subtext
	subtext = None
	st_textList = []
	subtextNode = None
	print("[0][GET SUB TEXT]")

	if mainArticleTag is not None:
		subtextNode = getTagWithAttrValue(mainArticleTag, 'div', 'class', 'highlights_wrap')

		if subtextNode is None:
			subtextNode = getTagWithAttrValue(mainArticleTag, 'div', 'class', 'story_highlight')

			if subtextNode is not None:
				for tag in subtextNode.descendants:
					try:
						if tag.name == 'a':
							st_textList.append(tag.get_text())
					except Exception as e:
						pass
		else:
			st_textNode = getTagWithAttrValue(subtextNode, 'div', 'class', 'lhs_highlights')

			for tag in st_textNode.descendants:
				try:
					if tag.name == 'li':
						st_textList.append(tag.string)
				except Exception as e:
					pass

	if subtextNode is not None:
		subtext = redditText.bold("HIGHLIGHTS")
		subtext += redditText.newline

		for line in st_textList:
			if line is None:
				continue
			subtext += redditText.lineNumber(line)
			subtext += redditText.newline

		subtextNode.decompose()
	else:
		print("[-1][GET SUB TEXT]")

	#get main text
	print("[0][GET MAIN TEXT]")

	if mainArticleTag is None:
		mainArticleTag = getTagWithAttrValue(soup, 'div', 'class', 'ins_storybody')
		if mainArticleTag is None:
			return None

	mainText = ''
	for tag in mainArticleTag.descendants:
		#extract text
		#prepare for reddit markdown
		try:
			name = tag.name
			if name == None:
				mainText += tag.string
			elif name == 'p':
				mainText += tag.string
				mainText += redditText.newline
			elif name == 'script':
				tag.clear()
			elif name == 'style':
				tag.clear()
			elif name == 'br':
				mainText += redditText.newline
			elif name == 'blockquote':
				q = ''
				for i in tag.contents:
					try:
						name = i.name
						if name == 'p':
							q += redditText.quote(i.get_text())
							q += redditText.newline
						elif name == None:
							q_lnk = redditText.link(i.string, tag.a['href'])
							q += redditText.quote(resolveShortURL(q_lnk))
						elif name == a:
							q += ' | ' + i.get_text()
					except Exception as e:
						pass
				mainText += redditText.newline
				mainText += q
				mainText += redditText.newline
				tag.clear()
		except Exception as e:
			print(e)
			pass

	mainText = mainText.replace(u'\xa0', ' ')
	mainText = mainText.replace('\r', ' ')
	mainText = redditText.safe(mainText)

	mainText.strip()

	if mainText == '':
		print("[-1][GET MAIN TEXT][ERROR]")

	print("[1][GET MAIN TEXT]")

	#get images
	print("[0][GET IMAGES]")
	images = []

	for tag in mainArticleTag.descendants:
		try:
			name = tag.name
			if name == 'img':
				images.append(tag['src'])
		except Exception as e:
			print(e)


	images = getImagesOfSize(images, MIN_IMAGE_SIZE)

	if images == []:
		print("[-1][GET IMAGES][ERROR][no images found on page]")

	#main image
	mainImageTag = getTagWithAttrValue(soup, 'img', 'id', 'story_image_main')

	if mainImageTag is not None:
		images.insert(0, mainImageTag['src'])
	else:
		mainImageTag = getTagWithAttrValue(soup, 'img', 'id', 'story_pic')
		if mainImageTag is not None:
			images.insert(0, mainImageTag.img['src'])

	#prepare for reddit markdown
	imageEntry = ''
	uniqueImages = list(set(images))
	for i in range(len(uniqueImages)):
		imageEntry += redditText.link('IMAGE ' + str(i+1), images[i])

		if i < len(images) - 1:
			imageEntry += ' | '

	if imageEntry == '':
		imageEntry = None

	print("[1][GET IMAGES]")

	extractedArticle = {
		"title" : title,
		"subtext": subtext,
		"text": mainText,
		"images" : imageEntry
	}

	print("[1][NDTV EXTRACTOR]")

	return extractedArticle

'''
u = 'http://sports.ndtv.com/olympics-2016/news/261721-rio-olympic-committee-threatens-to-cancel-sports-minister-vijay-goel-s-accreditation'

k = getArticle(u)

print(k['text'])
'''
