from datetime import datetime, timedelta

import praw

import auth

__version__ = '0.0.3'

def main():
    reddit = praw.Reddit(**auth.reddit)
    subreddit = reddit.subreddit('PurplePillTest')
    pos_actions = ['approvelink', 'approvecomment']
    neg_actions = ['removelink', 'removecomment', 'spamlink', 'spamcomment']
    all_actions = pos_actions + neg_actions
    days = 30
    users = {}
    for log in subreddit.mod.log():
        # Break out of loop if log entries are too old
        dt = datetime.fromtimestamp(log.created_utc)
        delta = dt - datetime.utcnow()
        if delta > timedelta(days=days):
            break
        # Filter actions
        if log.action not in all_actions:
            continue
        # Action counter
        users.setdefault(log.target_author, {})
        user = users[log.target_author]
        for action in all_actions:
            user.setdefault(action, 0)
        user[log.action] += 1
        # Positive/neagtive and total action counter
        user.setdefault('pos', 0)
        user.setdefault('neg', 0)
        user.setdefault('total', 0)
        if log.action in pos_actions:
            user['pos'] += 1
        elif log.action in neg_actions:
            user['neg'] += 1
        user['total'] += 1
    # Sort by total action count
    users = dict(sorted(users.items(), key=lambda u: u[1]['neg'], reverse=True))
    message = f'Mod log summary for the last {days} days:\n'
    for i, (user, counter) in enumerate(users.items()):
        message += '\n{}. {} | {} remove/spam | {} approve'.format(i+1, user, counter['neg'], counter['pos'])
    subreddit.message('Mod logs', message)

if __name__ == "__main__":
    main()
