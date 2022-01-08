import json
import pickledb
import tweepy
import pyjson5
import click
import csv as pycsv
import sys
from datetime import datetime
from email.utils import parsedate_tz

@click.group()
def main():
    '''\b
                                             /hsdh
                                   `+h/   .odo`/do
         --  /`                    +N/yd/sh/`:hs. 
         -Ns`yd.                    +m/-ym/:yy-   
          MMhhMm.                  .omds.-yNs`    
        `:MMMMMMmhs/-.           .oh+.`omy//yh:   
      `+dMMMMMMMMMMMNmh+-`     -sh+`  -yh:oysms   
     `yMMMMMMMMMMMMMMMMMNdo.`-yh/`  .sh/`  `--    
     +MMMMMMMMMMMMMMMMMMMMMNhh:`  `+d+`           
     dMMMMMMMMMMMMMMMMMMMMNh:   `/hs.             
     yMMMMMMMMMMMMMMMMMMMy-    :hh-               
     -NMMMMMMMMMMMMMMMMMM/   .yMMo                
      -mMMMMMMMMMMMMMMMMMNs:sNMMMMs               
        /hMMMMMMMMMMMMMMMMMMMMMMMMM+              
           -:oMMMMMMMMMMMMMMMMMMMMMM.             
            `dMMMMMMMMMMMMMMMMMMMMMMs             
           `yMMMMMMMMMMMMMMMMMMMMMMMm             
          .hMMMMMMMMMMMMMMMMMMMMMMMMM             
         /mMMMMMMMMMMMMMMMMMMMMMMMMMM             
       -hMMMMMMMMMMMMMMMMMMMMMMMMMMMm             
    `:hNMMMMMMMMMMMMMMMMMMMMNMMMMMMMs             
 `:smMMMMMMMMMMMMMMMMMMMMMMd:MMMMMMM.             
/dMMMMMMMMMNMMMMMMMNhMMMMNs` yMMMMMs              
 -/shdmdhs/oNMMMMNh:oNmdo-   /MMMMd`              
          -ydhys/.  --`      -MMMd`               
                             /MMy`                
                             yN/                  
                            .o`                   

               TweetDelete'''
    pass

@main.command("config", short_help="Configure settings for TweetDelete")
def config():
    with open ("config.json", "r") as read_file:
        settings = json.load(read_file)

    consumer_key = settings["api_key"]
    consumer_secret = settings["api_secret"]
    access_token = settings["access_token_key"]
    access_token_secret = settings["access_token_secret"]
    cutoff = settings["date_cutoff"]
    favorite_cutoff = settings["favorite_cutoff"]
    retweet_cutoff = settings["retweet_cutoff"]
    
    click.echo(f'''
CURRENT CONFIG
    
Delete tweets from before this date: {cutoff}
Save tweets with at least this many favs (0 = ignore favs): {favorite_cutoff}
Save tweets with at least this many retweets (0 = ignore retweets): {retweet_cutoff}
---------------------------''')
    
    if not consumer_key:
        consumer_key = input("Enter your Twitter API key: ")
    if not consumer_secret:
        consumer_secret = input("Enter your Twitter API secret: ")
    if not access_token:
        access_token = input("Enter your Twitter API access token: ")
    if not access_token_secret:
        access_token_secret = input("Enter your Twitter API access token secret: ")
    if not cutoff:
        cutoff = input("Delete all tweets from before this date (YYYY-MM-DD): ")

    choice = None
    
    while (choice != "y" and choice != "n"):
        choice = input("\nChange your date, fav, and retweet settings? [y/n]: ")
    if choice == "y":
        cutoff = input("Delete all tweets from before this date (YYYY-MM-DD): ")
        favorite_cutoff = int(input("Save tweets with at least this many favs (enter 0 to ignore favs): "))
        retweet_cutoff = int(input("Save tweets with at least this many retweets (or enter 0 to ignore retweets): "))
    
    json_object = {"api_key":consumer_key, "api_secret":consumer_secret, "access_token_key":access_token, "access_token_secret":access_token_secret, "date_cutoff":cutoff, "favorite_cutoff":favorite_cutoff, "retweet_cutoff":retweet_cutoff}
    
    with open ("config.json", "w") as write_file:
        json.dump(json_object, write_file, indent=4)


@main.command("tweets", short_help="Extract tweets from 'tweet.js' file and add them to a JSON-formatted database")
@click.option('--csv', is_flag=True, help='Add the --csv flag to export tweets to-be-deleted and to-be-saved to two CSV files')
def get_tweets(csv):
    try:
        with open("tweet.js", "r", encoding="utf8") as read_file:
            pos = read_file.readline().find("[")
            read_file.seek(pos)
            tweets = pyjson5.decode_io(read_file, some=False)
    except IOError:
        click.secho("\nERROR: Could not find 'tweet.js' file in this directory. Make sure to copy this file from your Twitter archive's Data folder.", fg='bright_yellow')
        click.echo("Exiting program...")
        sys.exit()

    with open ("config.json", "r") as read_file:
        settings = json.load(read_file)
        cutoff = settings["date_cutoff"]
        favorite_cutoff = settings["favorite_cutoff"]
        retweet_cutoff = settings["retweet_cutoff"]

    db = pickledb.load('tweets-todelete.db', False)

    if not db.get("tweetlist"):
        db.dcreate("tweetlist")

    date_cutoff = datetime.strptime(cutoff,'%Y-%m-%d')

    idelete = 0
    isave = 0
    
    if csv:
        with open('tweets-todelete.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = pycsv.writer(csvfile)
            writer.writerow(["ID", "Text", "Date", "Favorites", "Retweets"])
        with open('tweets-tosave.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = pycsv.writer(csvfile)
            writer.writerow(["ID", "Text", "Date", "Favorites", "Retweets"])
    
    for t in tweets:
        tweet = t["tweet"]
        timestamp = tweet["created_at"]
        time_tuple = parsedate_tz(timestamp.strip())
        tweet_date = datetime(*time_tuple[:6])
        tweet_favs = int(tweet["favorite_count"])
        tweet_retweets = int(tweet["retweet_count"])
        tweet_text = tweet["full_text"]
        if tweet_date < date_cutoff and (tweet_favs < favorite_cutoff or favorite_cutoff == 0) and (tweet_retweets < retweet_cutoff or retweet_cutoff == 0):
            click.echo(f"ADDED {tweet['id']} - {tweet_date}")
            db.dadd("tweetlist", (tweet['id'], False))
            if csv:
                with open('tweets-todelete.csv', 'a', newline='', encoding='utf-8') as csvfile:
                    writer = pycsv.writer(csvfile)
                    writer.writerow([tweet['id'], tweet_text, tweet_date, tweet_favs, tweet_retweets])
            idelete += 1
        elif tweet_date >= date_cutoff:
            click.echo(f"SKIPPED {tweet['id']} - too recent - {tweet_date}")
            if csv:
                with open('tweets-tosave.csv', 'a', newline='', encoding='utf-8') as csvfile:
                    writer = pycsv.writer(csvfile)
                    writer.writerow([tweet['id'], tweet_text, tweet_date, tweet_favs, tweet_retweets])
            isave += 1
        else:
            click.echo(f"SKIPPED {tweet['id']} - too many favs ({tweet_favs}) or RTs ({tweet_retweets}) - {tweet_date}")
            if csv:
                with open('tweets-tosave.csv', 'a', newline='', encoding='utf-8') as csvfile:
                    writer = pycsv.writer(csvfile)
                    writer.writerow([tweet['id'], tweet_text, tweet_date, tweet_favs, tweet_retweets])
            isave += 1
    
    click.echo(f"{idelete} tweets identified for deletion.")
    click.echo(f"{isave} tweets excluded.")
    
    db.dump()


@main.command("delete", short_help="Delete the tweets that were added to the database")
def delete():
    with open ("config.json", "r") as read_file:
        settings = json.load(read_file)
        consumer_key = settings["api_key"]
        consumer_secret = settings["api_secret"]
        access_token = settings["access_token_key"]
        access_token_secret = settings["access_token_secret"]
    
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)
    
    try:
        api.verify_credentials()
    except:
        click.secho("\nERROR: Could not verify the supplied credentials. Double-check the API key and access token information provided in 'config.json'.", fg='bright_yellow')
        click.echo("Exiting program...")
        sys.exit()
    
    db = pickledb.load('tweets-todelete.db', False)
    
    if not db.get("tweetlist"):
        click.secho("\nERROR: Could not find list of tweets to delete. Run the 'tweets' command before running the 'delete' command.", fg='bright_yellow')
        click.echo("Exiting program...")
        sys.exit()
    
    delete_list = db.dgetall("tweetlist")

    i = 0

    for d in delete_list:
        if delete_list[d] == False: # True = already processed/deleted, in case you stop the program and want to resume later
            click.echo(f"DELETING TWEET: {d}")
            try:
                api.destroy_status(d)
                db.dadd("tweetlist", (d, True))
                i += 1
            except:
                click.secho(f"FAILED TO DELETE TWEET {d}: NOT FOUND OR COULD NOT BE DELETED", fg='bright_yellow')
                db.dadd("tweetlist", (d, True))

    db.dump()

    click.echo(f"Total Deleted: {i}")


@main.command("help", short_help="Display detailed help and instructions")
def help():
    click.secho('\nTweetDelete Help & Instructions\n', fg='bright_cyan')
    click.echo('''See the Github page for easier-to-read instructions.

For this program to work, you'll need the following:

1. A copy of 'tweet.js' from a downloaded archive of your Twitter data. 
You can request this archive through your account settings on Twitter.

2. An API key and secret from the Twitter Developer Portal.

3. An access token and secret from the Twitter Developer Portal.

Place the 'tweet.js' file in this program's directory.

Edit 'config.json' or run 'untweet.py config' to enter your API 
key and access token details, as well as the date you want to delete 
tweets from before, and if you want to save any tweets based on number 
of favs or retweets.

Run 'untweet.py tweets' to extract the tweets from 'tweet.js'. Or, 
run 'untweet.py tweets --csv' to additionally save the results to 
two CSV files for review.\n''')
    click.secho('''AFTER COMPLETING THE NEXT STEP, ALL TWEETS DESIGNATED FOR DELETION WILL BE 
PERMANENTLY REMOVED FROM YOUR TWITTER ACCOUNT. 

Review your settings carefully. Export the deletion list to CSV and review 
the file if you have any doubts.\n''', fg='bright_red')
    click.echo("Run 'untweet.py delete' to delete the designated tweets from your account.\n")
    click.echo("Congratulations! You're free!")
if __name__ == "__main__":
    main()