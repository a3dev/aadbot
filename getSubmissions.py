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
            isRelevant = True

            #check if the bot is active on the domain
            parsedURL = tldextract.extract(submission.url)
            domain = parsedURL.domain + '.' + parsedURL.suffix
            isRelevant = isRelevant and domains.isActiveOnDomain(domain, subName)

            #check if the bot ignores the user
            isRelevant = isRelevant and not users.isIgnored(submission.author.name)

            if not isRelevant:
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
