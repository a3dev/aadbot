import praw

try:
    import env
except ModuleNotFoundError as e:
    print("env.py file not found")
    print("env.py contains keys needed to use reddit API.")
    print("praw is used, see here for more info : https://praw.readthedocs.io/en/latest/getting_started/authentication.html ")
    print("exiting...")
    exit()


def redditInstance():
    reddit = praw.Reddit(
        user_agent=env.user_agent,
        client_id=env.client_id,
        client_secret=env.client_secret,
        username=env.username,
        password=env.password
    )

    return reddit
