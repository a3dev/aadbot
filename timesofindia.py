import requests
from pprint import pprint
import pickle
from bs4 import BeautifulSoup
import json
import redditText
import urllib.parse

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

def getArticle(url):
	print("[0][TIMES OF INDIA EXTRACTOR]")

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

	#get title
	print("[0][GET TITLE]")

	title = None

	titleTag = getTagWithAttrValue(soup, 'h1', 'itemprop', 'headline')

	if titleTag is None or titleTag.string == '':
		titleTag = getTagWithAttrValue(soup, 'h2', 'class', 'media-heading')
		if titleTag is None or titleTag.string == '':
			print("[-1][GET TITLE][ERROR][not found]")

	if titleTag is not None:
		title = redditText.bold(titleTag.string)

	print(title)
	print("[1][GET TITLE]")

	#get subtext
	print("[0][GET SUB TEXT]")

	subtext = None

	subtextNode = getTagWithAttrValue(soup, 'section', 'class', 'highlight')

	if subtextNode is not None:
		st_headingNode = getTagWithAttrValue(subtextNode, 'h4', 'class', 'heading4')
		if st_headingNode is not None:
			st_heading = st_headingNode.get_text()

			st_textNode = subtextNode.artsummary

			st_textList = []

			for tag in st_textNode.descendants:
				try:
					if tag.name == 'li':
						st_textList.append(tag.get_text())
				except Exception as e:
					pass

			subtext = redditText.bold(st_heading)
			subtext += redditText.newline

			pprint(st_textList)

			if st_textList is not []:
				for line in st_textList:
					if line is None:
						continue
					subtext += redditText.lineNumber(line)
					subtext += redditText.newline
	#get main article node
	print("[0][GET MAIN NODE OF THE ARTICLE]")
	mainArticleTag = getTagWithAttrValue(soup, 'div', 'class', 'normal')

	if mainArticleTag is None:
		mainArticleTag = getTagWithAttrValue(soup, 'div', 'class', 'content')

		if mainArticleTag is None:
			print("[-1][GET MAIN NODE OF THE ARTICLE][ERROR]")
			return None

	print("[1][GET MAIN NODE OF THE ARTICLE]")

	#get main text

	print("[0][GET MAIN TEXT]")

	mainText = ''
	skip = False
	for tag in mainArticleTag.descendants:
		#extract text
		#prepare for reddit markdown
		try:
			name = tag.name
			#print(name, tag.attrs)
			if skip:
				if name == 'span' and 'nic_handler' in tag.attrs['class']:
					skip = False
				else:
					continue
			if name == 'div' and 'nic_wrapper' in tag.attrs['class']:
				#remove the newline character and trailing spaces
				esc_n = mainText.rfind('\n')
				mainText = mainText[:esc_n] + ' '
				skip = True
			elif name == None:
				mainText += (tag.string).strip()
			elif name == 'p':
				mainText += tag.string
				mainText += redditText.newline
			elif name == 'br':
				mainText += redditText.newline
		except Exception as e:
			pass

	mainText = mainText.replace('+\n  ', '')

	if mainText == '':
		print("[-1][GET MAIN TEXT][ERROR]")

	print("[1][GET MAIN TEXT]")

	#get images
	blacklist = ['http://timesofindia.indiatimes.com/photo/29439462.cms']
	print("[0][GET IMAGES]")

	fullArticleTag = getTagWithAttrValue(soup, 'div', 'class', 'main-content')

	if fullArticleTag is None:
		fullArticleTag = mainArticleTag

	images = []

	abs_image_url = lambda image_url: urllib.parse.urljoin(url, image_url)

	for tag in fullArticleTag.descendants:
		try:
			name = tag.name
			if name == 'img':
				image_url = abs_image_url(tag['src'])
				if image_url not in blacklist:
					images.append(image_url)
		except Exception as e:
			print(e)


	images = getImagesOfSize(images, MIN_IMAGE_SIZE)

	if images == []:
		print("[-1][GET IMAGES][ERROR][no images found on page]")

	#main image
	mainImageTag = getTagWithAttrValue(soup, 'img', 'id', 'story_image_main')

	if mainImageTag is not None:
		image_url = abs_image_url(mainImageTag['src'])
		images.insert(0, image_url)

	#prepare for reddit markdown
	imageEntry = ''
	for i in range(len(set(images))):
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
	print("[1][TIMES OF INDIA EXTRACTOR]")

	return extractedArticle

'''
u = 'http://timesofindia.indiatimes.com/city/delhi/Mutual-funds-to-become-costlier-on-GST-implementation/articleshow/53597776.cms'

k = getArticle(u)

print(k['text'])
'''
