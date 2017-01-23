import db

def isIgnored(username):
    db.connect("bot_db")

    userBlacklist = db.getIgnoredUsers()

    if username in userBlacklist:
        return True
    else:
        return False

def ignore(username):
    db.connect("bot_db")
    db.ignoreUser(username)

def unignore(username):
    db.connect("bot_db")
    db.unIgnoreUser(username)
