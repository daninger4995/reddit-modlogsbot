from datetime import datetime, timedelta

import praw

import auth

__version__ = '0.0.2'

def main():
    reddit = praw.Reddit(**auth.reddit)
    subreddit = reddit.subreddit('PurplePillTest')
    actions = ['approvelink', 'approvecomment', 'removelink', 'removecomment', 'spamlink', 'spamcomment']
    users = {}
    for log in subreddit.mod.log():
        dt = datetime.fromtimestamp(log.created_utc)
        delta = dt - datetime.utcnow()
        if delta > timedelta(days=30):
            break
        if log.action not in actions:
            continue
        users.setdefault(log.target_author, {})
        for action in actions:
            users[log.target_author].setdefault(action, 0)
        users[log.target_author][log.action] += 1
    print(users)

if __name__ == "__main__":
    main()
