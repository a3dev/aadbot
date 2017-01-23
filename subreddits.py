import db

def add(subName):
    db.connect('bot_db')
    db.addSubreddit(subName)

def remove(subName):
    db.connect('bot_db')
    db.removeSubreddit(subName)

def isAdded(subName):
    db.connect('bot_db')
    activeSubredditList = db.getActiveSubreddits()

    print(subName, activeSubredditList, subName in activeSubredditList)

    if subName in activeSubredditList:
        return True
    else:
        return False

def getActiveSubreddits():
    db.connect('bot_db')
    activeSubredditList = db.getActiveSubreddits()

    return activeSubredditList
