# Untweet

A tool for deleting your old tweets.

It actually works!™

Inspired by [semiphemeral](https://github.com/micahflee/semiphemeral), which is simpler to use but (in my experience) falls victim to the Twitter API only returning the user's most recent 3000-ish tweets rather than their full history.


## Prerequisites

- Python 3.x
- A copy of your [Twitter archive](https://help.twitter.com/en/managing-your-account/how-to-download-your-twitter-archive), specifically the `tweet.js` file contained within.
- A [Twitter API key](https://developer.twitter.com/en/docs/twitter-api/getting-started/getting-access-to-the-twitter-api), secret, and set of access tokens.

Copy the `tweet.js` file into the working directory of this program.


## Configuration

Run `pip install -r requirements.txt` to install the required Python packages.

Edit `config.json` or run `untweet.py config` to configure your settings:

- `api_key` - Twitter API key
- `api_secret` - Twitter API secret
- `access_token_key` - Twitter Access Token key
- `access_token_secret` - Twitter Access Token secret
- `date_cutoff` - Delete all tweets before this date
- `favorite_cutoff` - Save tweets with at least this many favorites (enter 0 to ignore favorites)
- `retweet_cutoff` - Save tweets with at least this many retweets (enter 0 to ignore retweets)


## Usage

Run `untweet.py tweets` to extract the tweets from `tweet.js`. Or, run `untweet.py tweets --csv` to additionally save the results to 
two CSV files. You can review the CSV files to see exactly which tweets will be deleted or saved.

**AFTER COMPLETING THE NEXT STEP, ALL TWEETS DESIGNATED FOR DELETION WILL BE PERMANENTLY REMOVED FROM YOUR TWITTER ACCOUNT.**

Run `untweet.py delete` to delete the designated tweets from your account.

Bask in the warm glow of obliteration.


## License

Licensed under the [Anti-Capitalist Software License (ACSL)](https://anticapitalist.software/). See the `LICENSE` file for full statement.
