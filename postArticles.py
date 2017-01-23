import praw
from pprint import pprint

import setSubmissions
import extractText
import redditText

def prepareComment(commentDict):
    comments = []

    text = commentDict['text']
    subtext = commentDict['subtext']
    title = commentDict['title']
    images = commentDict['images']
    botText = commentDict['botText']
    credit = commentDict['credit']

    if title is not None:
        commentText = title + redditText.hline
    if subtext is not None:
        commentText += subtext + redditText.hline
    if images is not None:
        commentText += images + redditText.hline

    if text is not None and len(text) == 1:
        commentText += text[0] + redditText.hline
    elif len(text) > 1:
        #reddit commment length is limited; so large text is divided into smaller postArticles
        #TODO: commment chains for large swathes of text
        for item in text:
            commentText += item

    if botText is not None:
        commentText += botText + redditText.hline
    if credit is not None:
        commentText += credit

    return commentText


def processLink(link):
    commentDict = extractText.getArticleText(link)

    commentText = prepareComment(commentDict)

    return commentText

def postComment(submissionsList, reddit):
    for submission_data in submissionsList:
        id_value = submission_data['id']
        link = submission_data['url']

        print("[INFO]id=", id_value)
        setSubmissions.submissionProcessed(id_value)

        try:
            commentText = processLink(link)
            submission = reddit.submission(id=id_value)
            print("[INFO]Posting the article text as a comment...")
            submission.reply(commentText)
        except Exception as e:
            print("[ERR]postArticles::postComment:Cannot proccess submission : ", id_value, " : ", e)
        else:
            setSubmissions.submissionSuccess(id_value)
