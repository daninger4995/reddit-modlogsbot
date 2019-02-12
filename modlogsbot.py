from datetime import datetime, timedelta

import praw

import auth

__version__ = '0.0.4'

def main():
    print('Initializing reddit...')
    reddit = praw.Reddit(**auth.reddit)
    subreddit = reddit.subreddit('PurplePillTest')
    pos_actions = ['approvelink', 'approvecomment']
    neg_actions = ['removelink', 'removecomment', 'spamlink', 'spamcomment']
    all_actions = pos_actions + neg_actions
    days = 30
    users = {}
    for i, log in enumerate(subreddit.mod.log(limit=None)):
        print(f'\rAnalysing logs... {i}', end='')
        # Break out of loop if log entries are too old
        dt = datetime.fromtimestamp(log.created_utc)
        delta = datetime.utcnow() - dt
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
    print('\nSorting data...')
    users = dict(sorted(users.items(), key=lambda u: u[1]['neg'], reverse=True))
    print('Building mod mail message...')
    message = f'Mod log summary for the last {days} days:\n'
    for i, (user, counter) in enumerate(users.items()):
        message += '\n{}. {} | {} remove/spam | {} approve'.format(i+1, user, counter['neg'], counter['pos'])
    print('Seding message...')
    subreddit.message('Mod logs', message)

if __name__ == "__main__":
    main()
