import os
from pprint import pprint

import sqlite3

sub_log = 'submissions_log'
sub_table = "submissions"

pm_table = 'privateMessages'
pm_log = 'privateMessages_log'


cRep_table = 'commentReplies'
cRep_log = 'commentReplies_log'

ignored_users_table = 'ignoredUsers'

domains_table = 'domains'

active_subreddit_table = 'subreddit_list'

db_path = None
def connect(db_name):
    global db_path
    db_path = 'database/' + db_name + '.sqlite'

    try:
        db_is_new = not os.path.exists(db_path)

        if db_is_new:
            print('INFO : Creating Database for the first time...')
            with sqlite3.connect(db_path) as conn:
                schema_filename = 'database/schema.sql'
                with open(schema_filename, 'rt') as f:
                    schema = f.read()
                    conn.executescript(schema)
        '''
        else:
            print('INFO : Database found : ', db_path)
        '''

    except Exception as e:
        db_path = None
        print('error establishing db connection : ', e)


def setSubmission(data, processed = False, failed = True):
    id_value = data['id']
    url = data['url']
    title = data['title']
    created_utc = data['created_utc']
    author = data['author']

    if db_path is None:
        print("ERROR : DB : setSubmission: ", 'db_path is None')
        exit()

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        try:
            #insert into submissions_table
            query = "INSERT INTO " + sub_table + " (id, url, title, created_utc, author) VALUES (?, ?, ?, ?, ?)"
            cursor.execute(query, (id_value, url, title, created_utc, author))

            #insert into submissions_log
            query = "INSERT INTO " + sub_log + " (id, processed, failed) VALUES (?, ?, ?)"
            cursor.execute(query, (id_value, processed, failed))

        except sqlite3.IntegrityError:
            print('ERROR: ID already exists in PRIMARY KEY column : ', id_value)

def setPrivateMessages(dataList, processed = False, isBot = False, failed = True):
    if db_path is None:
        print("ERROR : DB : setPrivateMessage: ", 'db_path is None')
        exit()

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        for data in dataList:
            id_value = data['id']
            subject = data['subject']
            body = data['body']
            author = data['author']

            try:

                #insert into privateMessages table
                query = "INSERT INTO " + pm_table + " (id, subject, body, author) VALUES (?, ?, ?, ?)"
                cursor.execute(query, (id_value, subject, body, author))

                #insert into privateMessages log
                query = "INSERT INTO " + pm_log + " (id, processed, isBOt, failed) VALUES (?, ?, ?, ?)"
                cursor.execute(query, (id_value, processed, isBot, failed))

            except sqlite3.IntegrityError:
                print('ERROR : DB : setCommentReply: ID already exists in PRIMARY KEY column : ', id_value)


def setCommentReplies(dataList, processed = False, isCommand = False, isCompliment = False,  failed = True):
    if db_path is None:
        print("ERROR : DB : setCommentReply: ", 'db_path is None')
        exit()

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        for data in dataList:
            id_value = data['id']
            context = data['context']
            subreddit = data['subreddit']
            body = data['body']
            author = data['author']

            try:
                #insert into commentReplies table
                query = "INSERT INTO " + cRep_table + " (id, subreddit, context, body, author) VALUES (?, ?, ?, ?, ?)"
                cursor.execute(query, (id_value, subreddit, context, body, author))
            except sqlite3.IntegrityError:
                print('ERROR : DB : setCommentReply: ID already exists in PRIMARY KEY column : ', id_value)

            try:
                #insert into commentReplies log
                query = "INSERT INTO " + cRep_log + " (id, processed, isCommand, isCompliment, failed) VALUES (?, ?, ?, ?, ?)"
                cursor.execute(query, (id_value, processed, isCommand, isCompliment, failed))
            except Exception as e:
                print('ERROR : DB : setCommentReply_log : ', e)


def updateSubmission(data):
    id_value = data['id']
    columns = ['processed', 'failed']

    if db_path is None:
        print("ERROR : DB : updateSubmission: ", 'db_path is None')
        exit()

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            for column in columns:
                if column in data:
                    query = "UPDATE " + sub_log + " SET " + column + " = ? WHERE id = ?"
                    cursor.execute(query, (data[column], id_value))

    except Exception as e:
        print("ERROR: Failed to update SUBMISSION LOG : " , e)

def updatePrivateMessage(data):
    id_value = data['id']
    columns = ['processed', 'isBot', 'failed']

    if db_path is None:
        print("ERROR : DB : updatePrivateMessage: ", 'db_path is None')
        exit()

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        for column in columns:
            if column in data:
                try:
                    query = "UPDATE " + pm_log + " SET " + column + " = ? WHERE id = ?"
                    cursor.execute(query, (data[column], id_value))

                except Exception as e:
                    print("ERROR: Failed to update PRIVATE MESSAGES LOG : " , e)


def updateCommentReply(data):
    id_value = data['id']
    columns = ['processed', 'isCompliment', 'isCommand', 'failed']

    if db_path is None:
        print("ERROR : DB : updateCommentReply: ", 'db_path is None')
        exit()

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            for column in columns:
                if column in data:
                    query = "UPDATE " + cRep_log + " SET " + column + " = ? WHERE id = ?"
                    cursor.execute(query, (data[column], id_value))

    except Exception as e:
        print("ERROR: Failed to update COMMENT REPLY LOG : " , e)

def getNewSubmissions():
    newSubmissions = []
    ids = []

    if db_path is None:
        print("ERROR : DB : getNewSubmissions: ", 'db_path is None')
        exit()

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        query = "SELECT id FROM " + sub_log + " WHERE processed = ? AND failed = ?"
        cursor.execute(query, ('0', '1'))

        for row in cursor.fetchall():
            id_value, = row
            ids.append(id_value)

        for id_value in ids:
            query = "SELECT id, url, title, created_utc, author FROM " + sub_table + " WHERE id = ?"
            cursor.execute(query, (id_value,))

            for row in cursor.fetchall():
                newSubmissions.append(
                    {
                        'id' : row[0],
                        'url' : row[1],
                        'title' : row[2],
                        'created_utc' : row[3],
                        'author' : row[4]
                    }
                )

    return newSubmissions

def getNewCommentReplies(subName):
    newCommentReplies = []
    ids = []

    if db_path is None:
        print("ERROR : DB : getNewCommentReplies: ", 'db_path is None')
        exit()

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        query = "SELECT id FROM " + cRep_log + " WHERE processed = ? AND failed = ?"
        cursor.execute(query, ('0', '1'))

        for row in cursor.fetchall():
            id_value, = row
            ids.append(id_value)

        for id_value in ids:
            query = "SELECT id, subreddit, context, body, author FROM " + cRep_table + " WHERE subreddit = ? AND  id = ?"
            cursor.execute(query, (subName, id_value,))

            for row in cursor.fetchall():
                newCommentReplies.append(
                    {
                        'id' : row[0],
                        'subreddit' : row[1],
                        'context' : row[2],
                        'body' : row[3],
                        'author' : row[4]
                    }
                )

    return newCommentReplies

def getNewPrivateMessages():
    newPrivateMessages = []
    ids = []

    if db_path is None:
        print("ERROR : DB : getNewMessages: ", 'db_path is None')
        exit()

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        query = "SELECT id FROM " + pm_log + " WHERE processed = ? AND failed = ?"
        cursor.execute(query, ('0', '1'))

        for row in cursor.fetchall():
            id_value, = row
            ids.append(id_value)

        for id_value in ids:
            query = "SELECT id, subject, body, author FROM " + pm_table + " WHERE id = ?"
            cursor.execute(query, (id_value,))

            for row in cursor.fetchall():
                newPrivateMessages.append(
                    {
                        'id' : row[0],
                        'subject' : row[1],
                        'body' : row[2],
                        'author' : row[3]
                    }
                )

    return newPrivateMessages

def setDomains(domainList):
    if db_path is None:
        print("ERROR : DB : setDomains: ", 'db_path is None')
        exit()
    blacklisted = 0

    for domain in domainList:

        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()

                query = "INSERT INTO " + domains_table + " (domain, blacklisted) VALUES (?, ?)"
                cursor.execute(query, (domain, blacklisted,))

        except sqlite3.IntegrityError:
            print('ERROR: Cannot INSERT domain, already exists: ', domain)

def unsetDomains(domainList):
    if db_path is None:
        print("ERROR : DB : unsetDomains: ", 'db_path is None')
        exit()

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            query = "DELETE FROM " + domains_table + " WHERE domain = ?"

            for domain in domainList:
                cursor.execute(query, (domain,))

    except Exception as e:
        print("ERROR: Failed to delete in DOMAINS TABLE : " , e)

def blacklistDomain(domainList):
    if db_path is None:
        print("ERROR : DB : blacklistDomain: ", 'db_path is None')
        exit()

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            query = "UPDATE " + domains_table + " SET blacklisted = '1' WHERE domain = ?"

            for domain in domainList:
                cursor.execute(query, (domain))

    except Exception as e:
        print("ERROR: Failed to update DOMAINS TABLE : " , e)


def getRelevantDomains():
    domainsList = []

    if db_path is None:
        print("ERROR : DB : getRelevantDomains: ", 'db_path is None')
        exit()

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        query = "SELECT domain FROM " + domains_table + " WHERE blacklisted = ?"
        cursor.execute(query, ('0'))

        for row in cursor.fetchall():
            domain, = row
            domainsList.append(domain)

    return domainsList

def getBlacklistedDomains():
    domainsList = []

    if db_path is None:
        print("ERROR : DB : getBlacklistedDomains: ", 'db_path is None')
        exit()

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        query = "SELECT domain FROM " + domains_table + " WHERE blacklisted = ?"
        cursor.execute(query, ('1'))

        for row in cursor.fetchall():
            domain, = row
            domainsList.append(domain)


    return domainsList

def ignoreUser(username):
    if db_path is None:
        print("ERROR : DB : ignoreUser: ", 'db_path is None')
        exit()

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            query = "INSERT INTO " + ignored_users_table + " (username) VALUES (?)"
            cursor.execute(query, (username,))

    except Exception as e:
        print("ERROR: Failed to ignore user" + username + " : " , e)

def unIgnoreUser(username):
    if db_path is None:
        print("ERROR : DB : unIgnoreUser: ", 'db_path is None')
        exit()

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            query = "DELETE FROM " + ignored_users_table + " WHERE username = ?"
            cursor.execute(query, (username,))

    except Exception as e:
        print("ERROR: Failed to unignore user" + username + " : " , e)

def getIgnoredUsers():
    ignoredUserList = []

    if db_path is None:
        print("ERROR : DB : getIgnoredUsers: ", 'db_path is None')
        exit()

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        query = "SELECT * FROM " + ignored_users_table
        cursor.execute(query)

        for row in cursor.fetchall():
            user, = row
            ignoredUserList.append(user)

    return ignoredUserList

def addSubreddit(subName):
    if db_path is None:
        print("ERROR : DB : blacklistUser: ", 'db_path is None')
        exit()

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            query = "INSERT INTO " + active_subreddit_table + " (subName) VALUES (?)"
            cursor.execute(query, (subName,))

    except Exception as e:
        print("ERROR: Failed to add subreddit " + subName + " : " , e)

def removeSubreddit(subName):
    if db_path is None:
        print("ERROR : DB : removeSubreddit: ", 'db_path is None')
        exit()

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            query = "DELETE FROM " + active_subreddit_table + " WHERE subName = ?"
            cursor.execute(query, (subName,))

    except Exception as e:
        print("ERROR: Failed to remove subreddit" + subName + " : " , e)

def getActiveSubreddits():
    activeSubreddits = []

    if db_path is None:
        print("ERROR : DB : activeSubreddits: ", 'db_path is None')
        exit()

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        query = "SELECT * FROM " + active_subreddit_table
        cursor.execute(query)

        for row in cursor.fetchall():
            subreddit, = row
            activeSubreddits.append(subreddit)

    return activeSubreddits
