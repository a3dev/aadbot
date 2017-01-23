import requests
from pprint import pprint
import json
import redditText

from newspaper import Article

def getArticle(url):

	print("[0][NEWSPAPER3K EXTRACTOR]")

	try:
		article = Article(url)
		article.download()
	except Exception as e:
		print("[-1][NEWSPAPER3K EXTRACTOR][CANNOT DOWNLOAD ARTICLE][ERR] :", e)
		return None

	article.parse()

	title = redditText.bold(article.title)

	imageEntry = ""
	if article.top_image is not None:
		imageEntry = redditText.link('IMAGE', article.top_image)

	text = article.text

	credit = redditText.superscript("Powered by") + " " + redditText.link(redditText.superscript("newspaper3k"), "https://github.com/codelucas/newspaper")

	extractedArticle = {
		"title" : title,
		"subtext" : None,
		"images" : imageEntry,
		"text" : text,
		"credit" : credit
	}

	print("[1][NEWSPAPER3K EXTRACTOR]")

	return extractedArticle
