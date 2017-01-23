import time
from pprint import pprint

import login
import getSubmissions
import inbox
import postArticles
import comments
import pms
import subreddits

reddit = login.redditInstance()

activeSubredditList = subreddits.getActiveSubreddits()
print("#################################################")
print("active on the followin subreddits : ")
pprint(activeSubredditList)
print("#################################################")
for subName in activeSubredditList:
    print("=================================================")
    print("=================================================")
    print("[INFO]WORKING ON SUBREDDIT : ", subName)
    print("=================================================")

    print("[INFO]Getting new submissions...")
    print(".................................................")
    submissionsList = getSubmissions.newSubmissions(subName, reddit)

    print("[INFO]Processing submissions...")
    print(".................................................")
    postArticles.postComment(submissionsList, reddit)

    print("[INFO]Cheking Inbox for comment replies...")
    print(".................................................")
    ReplyList = inbox.getNewCommentReplies(subName, reddit)

    print("[INFO]Cheking Inbox for private messages...")
    print(".................................................")
    PMList = inbox.getNewPrivateMessages(reddit)

    comments.process(ReplyList, subName, reddit)
    pms.process(PMList, reddit)
