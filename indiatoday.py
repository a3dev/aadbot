import requests
from pprint import pprint
import pickle
from bs4 import BeautifulSoup
import json
import redditText

#constants

MIN_IMAGE_SIZE = 9000 #bytes

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

def getArticle(url):
	print("[0][INDIA TODAY EXTRACTOR]")

	print("url : ", url)


	r = requests.get(url)
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

	#get main article node
	print("[0][GET MAIN NODE OF THE ARTICLE]")
	mainArticleTag = getTagWithAttrValue(soup, 'div', 'class', 'strleft')

	if mainArticleTag is None:
		print("[-1][GET MAIN NODE OF THE ARTICLE][ERROR]")

	print("[1][GET MAIN NODE OF THE ARTICLE]")

	#get title
	print("[0][GET TITLE]")

	title = None

	titleTag = mainArticleTag.h1

	if titleTag is None or titleTag.string == '':
		print("[-1][GET TITLE][ERROR][not found]")
	else:
		title = redditText.bold(titleTag.string)

	print(title)
	print("[1][GET TITLE]")


	#get subtext

	subtext = None

	print("[0][GET SUB TEXT]")

	subtext = ''

	subTextTag = mainArticleTag.h2

	if subTextTag is None or subTextTag.string == '':
		print("[-1][GET SUB TEXT][ERROR][not found]")
	else:
		subtext = subTextTag.string

	subtext = subtext.replace(u'\xa0', ' ')
	subtext = subtext.replace('\r', ' ')
	subtext = redditText.italics(subtext)

	#get story NODE

	mainArticleTag = getTagWithAttrValue(mainArticleTag, 'div', 'class', 'right-story-container')

	#get highlights

	subtextNode = getTagWithAttrValue(mainArticleTag, 'div', 'class', 'highlights-chunk')

	if subtextNode is not None:
		st_textList = []

		for tag in subtextNode.descendants:
			try:
				tagName = tag.name

				if tagName == 'div' and 'rgt_hl' in tag['class']:
						st_textList.append(tag.string)
			except Exception as e:
				pass

		if st_textList is not []:
			subtext += redditText.newline
			for line in st_textList:
				if line is None:
					continue
				subtext += redditText.lineNumber(line)
				subtext += redditText.newline

		subtextNode.decompose()

	print("[1][GET SUB TEXT]")

	#get main text
	print("[0][GET MAIN TEXT]")


	mainText = ''
	for tag in mainArticleTag.descendants:
		#extract text
		#prepare for reddit markdown
		try:
			name = tag.name
			if name == None:
				mainText += tag.string
			elif name == 'style':
				tag.clear()
			elif name == 'p':
				mainText += tag.string
				mainText += redditText.newline
			elif name == 'img':
				img_text = 'IMAGE'
				if tag.has_attr('alt') and tag['alt'] != '':
					img_text = tag['alt']
				img_link = tag['src']
				mainText += redditText.newline +  redditText.link(img_text, img_link) + redditText.newline
			elif name == 'br':
				mainText += redditText.newline
			elif name == 'blockquote':
				bq = ''
				for b_tag in tag.children:
					if b_tag.name == 'a':
						bq += redditText.link('TWEET', b_tag['href'])

				mainText += redditText.newline
				mainText += redditText.quote(bq)
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

	print(images)

	images = getImagesOfSize(images, MIN_IMAGE_SIZE)

	if images == []:
		print("[-1][GET IMAGES][ERROR][no images found on page]")

	#main image
	mainImageTag = getTagWithAttrValue(soup, 'img', 'id', 'story_image_main')

	if mainImageTag is not None:
		images.insert(0, mainImageTag['src'])
	else:
		mainImageNode = getTagWithAttrValue(soup, 'div', 'class', 'downloadstoryimg')
		if mainImageNode is not None:
			images.insert(0, mainImageNode.img['src'])

	#prepare for reddit markdown
	imageEntry = ''
	uniqueImages = list(set(images))
	for i in range(len(uniqueImages)):
		imageEntry += redditText.link('IMAGE ' + str(i+1), images[i])

		if i < len(images) - 1:
			imageEntry += ' | '

	print("[1][GET IMAGES]")

	extractedArticle = {
		"title" : title,
		"subtext": subtext,
		"text": mainText,
		"images" : imageEntry
	}

	print("[1][INDIA TODAY EXTRACTOR]")

	return extractedArticle

'''
u = 'http://indiatoday.intoday.in/story/nda-questions-rahul-gandhis-silence-over-caning-of-dalit-youths-in-bihar-stage-protest/1/733738.html'

k = getArticle(u)

print(k['text'])
'''
