from pprint import pprint

import db

bot_db = 'u_ anti_anti_adblock'

# get new items in INBOX
# classify if they are commands or compliments or other
# filter out messages that are already processed

def checkCommentReplies(reddit):
    replies = []
    db.connect('bot_db')


    for reply in reddit.inbox.comment_replies():
        if reply.new :
            replies.append(
                {
                    'author' : reply.author.name,
                    'body' : reply.body,
                    'context' : reply.context,
                    'subreddit' : (reply.context).split('/')[2],
                    'id' : reply.id
                }
            )
            print("[INFO]id=", reply.id, " body=", reply.body)
            reddit.inbox.mark_read([reply])
            print("\t\tmarked as read")
    db.setCommentReplies(replies)

def getNewCommentReplies(subName, reddit):
    db.connect('bot_db')
    print("[INFO]Checking for new comments...")
    checkCommentReplies(reddit)

    newCommentReplies = db.getNewCommentReplies(subName)

    return newCommentReplies

def updateCommentReply(data):
    db.updateCommentReply(data)

def commentProcssed(id_value):
    data = {
        'id' : id_value,
        'processed' : '1'
    }
    updateCommentReply(data)

def commentSucceded(id_value):
    data = {
        'id' : id_value,
        'failed' : '0'
    }
    updateCommentReply(data)


def checkPrivateMessages(reddit):
    pms = []

    db.connect('bot_db')

    for item in reddit.inbox.all():
        if item.new and 'Message' in repr(item) :
            pm = item
            pms.append(
                {
                    'author' : pm.author,
                    'subject' : pm.subject,
                    'body' : pm.body,
                    'id' : pm.id
                }
            )
            print("[INFO]id=", pm.id, " body=", pm.body)
            reddit.inbox.mark_read([pm])
            print("\t\tmarked as read")
    db.setPrivateMessages(pms)

def getNewPrivateMessages(reddit):
    db.connect('bot_db')
    checkPrivateMessages(reddit)

    newPrivateMessages = db.getNewPrivateMessages()

    return newPrivateMessages

def updatePrivateMessage(data):
    db.connect('bot_db')
    db.updatePrivateMessage(data)

def PMProcssed(id_value):
    data = {
        'id' : id_value,
        'processed' : '1'
    }
    updatePrivateMessage(data)

def PMSucceded(id_value):
    data = {
        'id' : id_value,
        'failed' : '0'
    }
    updatePrivateMessage(data)
