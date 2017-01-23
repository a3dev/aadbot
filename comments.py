from pprint import pprint

import domains
import inbox
import redditText as rt

BOT_NAME = 'anti_anti_adblock'

def process(data, subName, reddit):
    for item in data:
        author = item['author']
        body = item['body']
        context = item['context']
        id_value = item['id']

        inbox.commentProcssed(id_value)

        if body == 'delete' or body == 'remove' or body == 'su rm':

            #get the parent comment which is posted by the bot
            comment = reddit.comment(id_value)
            comment.refresh()
            botCommentID = comment.parent_id

            botComment = (reddit.comment(botCommentID[3:])).refresh()

            botCommentParentID = botComment.parent_id



            #check if it is the top comment = ariticle submission
            if 't3_' in botCommentParentID:

                submission = reddit.submission(botCommentParentID[3:])

                #check if it's the op
                if submission.author == author :
                    try:
                        botComment.delete()
                    except Exception as e:
                        print('comments::process: Cannot delete comment : ', botCommentID, ' : ', e)
                        replyText = 'An error occured while trying to delete the comment. You can report this here :  https://redd.it/4w5e2f. You may try and give the command again after sometime.'
                        comment.reply(replyText)
                    else:
                        inbox.commentSucceded(id_value)

        elif 'domains' in body:
            items = body.split(' ')

            if items[0] == 'domains':
                comment = reddit.comment(id_value)
                comment.refresh()

                replyText = 'user : ' + author + rt.newline
                replyText += 'cmd : ' + rt.codeSnippet(rt.safe(body)) + rt.newline

                if items[1] == '-l' or items[1] == '-list':
                    relevantDomains = domains.getRelevantDomains(subName)

                    replyText += 'I am active on these domains : ' + rt.newline

                    for domain in relevantDomains:
                        replyText += domain + ' | '

                    comment.reply(replyText)
                    inbox.commentSucceded(id_value)

                if items[1] == '-a' or items[1] == '-add':
                    if isMod(author, subName, reddit):
                        domainsToAdd = items[2].split(',')

                        try:
                            domains.setDomains(domainsToAdd, subName)
                        except Exception as e:
                            print('comments::process: Cannot add domains : ', domainsToAdd,' : ', e)

                            replyText = 'Failed to add any domains. You can report this here : https://redd.it/4w5e2f'
                            comment.reply(replyText)
                        else:
                            replyText += 'Active on the following domains : ' + rt.newline

                            relevantDomains = domains.getRelevantDomains(subName)

                            for domain in relevantDomains:
                                replyText += domain + ' | '

                            comment.reply(replyText)
                            inbox.commentSucceded(id_value)

                if items[1] == '-r' or items[1] == '-remove':
                    if isMod(author, subName, reddit):
                        domainsToRemove = items[2].split(',')

                        try:
                            domains.unsetDomains(domainsToRemove, subName)
                        except Exception as e:
                            print('comments::process: Cannot remove domains : ', domainsToRemove,' : ', e)

                            replyText = 'Failed to remove any domains. You can report this here : https://redd.it/4w5e2f'
                            comment.reply(replyText)
                        else:
                            replyText += 'Active on the following domains : ' + rt.newline

                            relevantDomains = domains.getRelevantDomains(subName)

                            for domain in relevantDomains:
                                replyText += domain + ' | '

                            comment.reply(replyText)
                            inbox.commentSucceded(id_value)


# this medthod shouldn't be here...
def isMod(redditorName, subName, reddit):
    for mod in reddit.subreddit(subName).moderator:
        if mod == redditorName:
            return True

    return False
