import tldextract

import db
import domains
import users


# get new submissions
# make sure they are new and not self posts
# filter out submissions that are already processed

RETRIELVAL_LIMIT = 20
def getSubmissions(subName, reddit):
    newSubmissions = []

    db.connect(subName)

    subreddit = reddit.subreddit(subName)

    relevantDomains = domains.getRelevantDomains(subName)

    print("Processing the following domains links only : ", relevantDomains)

    #for submission in subreddit.stream.submissions():
    for submission in subreddit.new(limit = RETRIELVAL_LIMIT):
        if not submission.is_self:
            #check if the bot is active on the domain
            parsedURL = tldextract.extract(submission.url)
            domain = parsedURL.domain + '.' + parsedURL.suffix
            inactiveOnDomain = not domains.isActiveOnDomain(domain, subName)

            #check if the bot ignores the user
            userIsIgnored = users.isIgnored(submission.author.name)

            #check if the submission is already in the database
            alreadyRecorded = isRecorded(submission.id)

            if inactiveOnDomain or userIsIgnored or alreadyRecorded:
                infoText = "[INFO]This submission is marked as irrelevant : "
                if inactiveOnDomain:
                    infoText = infoText + "<inactiveOnDomain>"
                if userIsIgnored:
                    infoText = infoText + "<userIsIgnored>"
                if alreadyRecorded:
                    infoText = infoText + "<alreadyRecorded>"

                infoText = infoText + " : "

                print(infoText, submission.id)

                #skip processing this submission
                continue

            newSubmissions.append(
                {
                    'id' : submission.id,
                    'title' : submission.title,
                    'url' : submission.url,
                    'created_utc' : submission.created_utc,
                    'author' : submission.author.name
                }
            )

            print("[INFO]Submission:: id=", submission.id, " title=", submission.title)

    for item in newSubmissions:
        db.setSubmission(item)

def newSubmissions(subreddit_name, reddit):
    getSubmissions(subreddit_name, reddit)

    newSubmissions = db.getNewSubmissions()

    return newSubmissions

def isRecorded(id_value):
    subName = 'india'
    db.connect(subName)
    return db.isSubmissionRecorded(id_value)
