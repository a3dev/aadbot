from pprint import pprint

import users
import subreddits
import redditText as rt
import inbox

BOT_NAME = 'anti_anti_adblock'

def process(data, reddit):
    for item in data:
        author = item['author']
        body = item['body']
        id_value = item['id']

        inbox.PMProcssed(id_value)

        greetingList = ['hi', 'hello', 'hey']
        actionList = [
            'I am a mod and I want ' + BOT_NAME + ' on my subreddit. Reply `ADD subreddit_name`',
            'I am a mod and I no longer want ' + BOT_NAME + ' on my subreddit. Reply `REMOVE subreddit_name`',
            'I want ' + BOT_NAME + ' to ignore my posts site wide.  Reply `IGNORE ME`',
            'I want ' + BOT_NAME + ' to stop ignoring my posts site wide. Reply `UNIGNORE ME`'
            ]

        pm = reddit.inbox.message(id_value)

        if body.lower() in greetingList:
            replyText = 'Hello, ' + author + '!' + rt.newline
            replyText += 'What would you like to do?' + rt.newline

            replyText += rt.lineNumber(actionList[0])
            replyText += rt.lineNumber(actionList[1])

            if users.isIgnored(author):
                replyText += rt.lineNumber(actionList[3])
            else:
                replyText += rt.lineNumber(actionList[2])

            replyText += rt.newline
            replyText += 'Do not add anything else to your reply.' + rt.newline

            pm.reply(replyText)
            inbox.PMSucceded(id_value)
        else:
            commandList = ['add', 'remove', 'ignore', 'unignore']
            term = body.split(' ')
            cmd = term[0].lower()

            if len(term) == 2:
                subName = term[1]
            else:
                continue

            if cmd in commandList:
                if cmd == 'add':
                    try:
                        subreddit_search_result = reddit.subreddits.search_by_name(subName, include_nsfw=True, exact=True)[0].display_name
                    except Exception as e:
                        replyText = 'ERROR : Cannot add the subreddit. Please make sure ' + rt.codeSnippet(subName) + ' exists.'
                        pm.reply(replyText)
                        inbox.PMSucceded(id_value)
                    else:
                        if subreddits.isAdded(subName):
                            replyText = rt.codeSnippet(subName) +  " has already been added. No further action required."

                            pm.reply(replyText)
                            inbox.PMSucceded(id_value)
                        else:
                            try:
                                subreddits.add(subName)
                            except Exception as e:
                                print('[ERR] pms::process: cannot add subreddit: ', e)
                                replyText = "Error. Unable to add subreddit at the moment. If you think this is a bug you can post it here: https://redd.it/4w5e2f"
                                pm.reply(replyText)
                            else:
                                replyText = BOT_NAME + ' is now active on ' + rt.codeSnippet(subName) + rt.newline

                                replyText += ' I will post articles from some default domains that are not adblocker unfriendly. You can change them to fit your subreddit.' + rt.newline

                                replyText += 'Check this out for more info : https://redd.it/4u2iwn. Thank you.'

                                pm.reply(replyText)
                                inbox.PMSucceded(id_value)
                elif cmd == 'remove':
                    if subreddits.isAdded(subName):
                        try:
                            subreddits.remove(subName)
                        except Exception as e:
                            print('[ERR] pms::process: cannot remove subreddit: ', e)
                            replyText = "Error. Unable to remove " + rt.codeSnippet(subName) + " at the moment. If you think this is a bug you can post it here: https://redd.it/4w5e2f"
                            pm.reply(replyText)
                        else:
                            pm.reply(BOT_NAME + ' will no longer be active on this subreddit : ' + rt.codeSnippet(subName))
                            inbox.PMSucceded(id_value)
                    else:
                        pm.reply(BOT_NAME + ' was not active on ' + rt.codeSnippet(subName) + '. No further action required.')
                        inbox.PMSucceded(id_value)

                elif cmd == 'ignore':
                    if users.isIgnored(author):
                        pm.reply("You are already being ignored by " + BOT_NAME + ". No further action required.")
                        inbox.PMSucceded(id_value)
                    else:
                        try:
                            users.ignore(author)
                        except Exception as e:
                            print('[ERR] pms::process: cannot remove subreddit: ', e)
                            replyText = "Error. Unable add " + rt.codeSnippet(author) + " to the ignore list at the moment. If you think this is a bug you can post it here: https://redd.it/4w5e2f"
                            pm.reply(replyText)
                        else:
                            pm.reply("Your posts will be ignored by " + BOT_NAME + ". You can send a " + rt.codeSnippet('Hi') + " to me if you change your mind.")
                            inbox.PMSucceded(id_value)
                elif cmd == 'unignore':
                    if users.isIgnored(author):
                        try:
                            users.unignore(author)
                        except Exception as e:
                            print('[ERR] pms::process: cannot remove subreddit: ', e)
                            replyText = "Error. Unable remove " + rt.codeSnippet(author) + " from the ignore list at the moment. If you think this is a bug you can post it here: https://redd.it/4w5e2f"
                            pm.reply(replyText)
                        else:
                            pm.reply("Your posts will no longer be ignored by " + BOT_NAME)
                            inbox.PMSucceded(id_value)
                    else:
                        pm.reply("You are currently not ignored by " + BOT_NAME + ". No further action required.")
                        inbox.PMSucceded(id_value)
