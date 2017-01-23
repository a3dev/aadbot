import requests
from pprint import pprint
import pickle
from bs4 import BeautifulSoup
import json
import redditText

#constants

MIN_IMAGE_SIZE = 9000

def getTagWithAttrValue(soup, tagName, attr, value):
	for element in soup.descendants:
		try:
			if element.name == tagName:
				if element.has_attr(attr):
					values =  element.attrs[attr]
					for item in values:
						if value == item.lower():
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
	print("[0][ECONOMIC TIMES EXTRACTOR]")

	print("url : ", url)


	r = requests.get(url)

	'''
	try:
		pickle.dump(r, open("page.p", "wb" ))
	except Exception as e:


	try:
		r = pickle.load(open("page.p", "rb"))
	except Exception as e:
		pass
		pass
	'''

	soup = BeautifulSoup(r.text, 'html.parser')

	#GET MAIN ARTICLE NODE
	print("[0][GET MAIL ARTICLE NODE]")

	article = soup.find("article")

	if article is None:
		print("[-1][GET MAIL ARTICLE NODE][ERROR][not found]")
		exit()

	print("[1][GET MAIL ARTICLE NODE]")

	#get TITLE
	print("[0][GET TITLE]")

	title = ''

	titleTag = getTagWithAttrValue(article, 'h1', 'class', 'title')

	if titleTag.string == '' or titleTag is None:
		print("[-1][GET TITLE][ERROR][not found]")
	else:
		title = redditText.bold(titleTag.string)

	print("[1][GET TITLE]")
	print(title)

	#get aritcle

	print("[0][GET MAIN TEXT]")

	mainTextTag = getTagWithAttrValue(article, 'div', 'class', 'normal')

	mainText = ''
	for tag in mainTextTag.descendants:
		try:
			name = tag.name
			if name == None:
				mainText += tag.string
			elif name == 'p':
				mainText += tag.string
				mainText += redditText.newline
			elif name == 'br':
				mainText += redditText.newline
			'''
			elif name == 'a':
				print(tag)
				linkText = tag.get_text()
				link = tag['href']
				mainText += redditText.link(linkText, link)
			'''
		except Exception as e:
			pass

	if mainText == '':
		print("[-1][GET MAIN TEXT][ERROR]")

	print("[1][GET MAIN TEXT]")

	#get images
	print("[0][GET IMAGES]")

	images = []

	for tag in article.descendants:
		try:
			name = tag.name
			if name == 'img':
				images.append(tag['src'])
		except Exception as e:
			print(e)


	images = getImagesOfSize(images, MIN_IMAGE_SIZE)

	if images == []:
		print("[-1][GET IMAGES][ERROR]")

	imageEntry = ''
	for i in range(len(images)):
		imageEntry += redditText.link('IMAGE ' + str(i+1), images[i])

		if i < len(images) - 1:
			imageEntry += ' | '

	pprint(images)
	print("[1][GET IMAGES]")

	extractedArticle = {
		"title" : title,
		"subtext":None,
		"text": mainText,
		"images" : imageEntry
	}

	print("[1][ECONOMIC TIMES EXTRACTOR]")
	return extractedArticle

'''
u = 'http://economictimes.indiatimes.com/news/politics-and-nation/arrest-me-in-six-months-or-i-will-arrest-you-after-six-months-kejriwal-to-majithia/articleshow/53448990.cms?'

k = getArticle(u)

pprint(k)
'''
