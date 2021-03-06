import os
import datetime
import slack
import praw
from flask import Flask

app = Flask(__name__)

bot_username = os.environ.get('BOT_USERNAME')
bot_client_id = os.environ.get('BOT_CLIENT_ID')
bot_client_secret = os.environ.get('BOT_CLIENT_SECRET')
slack_token = os.environ.get('SLACK_TOKEN')
slack_channel = os.environ.get('SLACK_CHANNEL_ID')
if bot_username is None or bot_client_id is None or bot_client_secret is None \
        or slack_token is None or slack_channel is None:
    print('need passwords and secrets and shit')
    exit(1)

user_string = os.environ.get('USER_LIST')
if len(user_string) < 1:
    print('need a list of users to follow')
    exit(1)
user_list = user_string.split(',')


@app.route("/")
def run():
    time_limit = datetime.datetime.utcnow() - datetime.timedelta(minutes=15)
    slack_client = slack.WebClient(token=slack_token)
    reddit = praw.Reddit(username=bot_username,
                         client_secret=bot_client_secret,
                         client_id=bot_client_id,
                         user_agent='Constable Reggie v0.0.1')
    for user in user_list:
        redditor = reddit.redditor(user)
        posts = {}
        for submission in redditor.submissions.new(limit=100):
            if submission.over_18:
                created = datetime.datetime.utcfromtimestamp(submission.created_utc)
                if created > time_limit:
                    # check if posts contains last piece of permalink, true=ignore, false=insert
                    if submission.title not in posts.keys():
                        posts[submission.title] = 'https://reddit.com{}'.format(submission.permalink)
        # post posts{} to slack
        if len(posts) > 0:
            message = 'https://reddit.com/user/{user}\n```{posts}```'
            slack_client.chat_postMessage(channel=slack_channel,
                                          text=message.format(user=user, posts='\n'.join(posts.values())))
    return "OK"


if __name__ == '__main__':
    port = os.environ.get('PORT', 5000)
    app.run(host='0.0.0.0', port=port)
