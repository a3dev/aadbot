import requests
from pprint import pprint
import pickle
from bs4 import BeautifulSoup
import json

import newspaper3k

import redditText
import prometheus


#reddit quirks
MAX_COMMENT_LENGTH = 9500

def propSplit(haystack, needle1, needle2, interval):
    text = {}
    key = lambda x: len(x.keys())

    if len(haystack) < interval:
        text[key(text)] = haystack
        return text


    hayList = haystack.split(needle1)

    part = ''
    for item in hayList:
        item_len = len(item)

        if len(part) + item_len < interval:
            part = part + needle1 + needle1 + item
        elif item_len > interval:
            text[key(text)] = needle1 + needle1 + part

            tparts = findAtPos(item, needle2, '', interval)

            text[key(text)] = needle1 + needle1
            for tpart in tparts:
                text[key(text)] = tparts[tpart]
        else:
            text[key(text)] = needle1 + needle1 + part
            part = item

    return(text)

def getArticleText(url):
    comment = {}

    res = None

    try:
        res = prometheus.getArticle(url)
    except Exception as e1:
        print("error - prometheus : ", e1)
        try:
            res = newspaper3k.getArticle(url)
        except Exception as e2:
            print("error - newspaper3k : ", e2)

    if res is None:
        print("extractText.py - FATAL ERROR")
        return None

    comment['title'] = res['title']
    comment['text'] = propSplit(redditText.safe(res['text']), '\n', ' ', MAX_COMMENT_LENGTH)
    comment['images'] = res['images']
    comment['subtext'] = res['subtext']
    comment['credit'] = res['credit']

    #bot_text
    bot_version = 'Version : 1.0a'
    bot_changelog = 'https://www.reddit.com/r/anti_anti_adblock/comments/5pr3ac/changelog/'
    bot_function = '''Function : I post the article's text as a comment if the website is adblocker unfriendly.'''
    bot_config_text = 'I accept commands!'
    bot_config_ref = 'https://www.reddit.com/r/anti_anti_adblock/comments/5pr33h/10a_commands_accepted_by_the_bot/'

    bot_text = redditText.superscript(bot_version) + " ^| "
    bot_text += redditText.link(redditText.superscript('Changelog'), bot_changelog)
    bot_text += redditText.newline
    bot_text += redditText.superscript(bot_function)
    bot_text += redditText.newline
    bot_text += redditText.link(redditText.superscript(bot_config_text), bot_config_ref)
    bot_text += redditText.newline

    comment['botText'] = bot_text

    return comment
