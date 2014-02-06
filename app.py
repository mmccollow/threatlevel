from flask import Flask, render_template, url_for
from twitter import Twitter, OAuth
from re import findall
from dateutil import parser
from datetime import datetime
import pytz

CONSUMER_KEY = 'redacted'
CONSUMER_SECRET = 'redacted'
oauth_token = 'redacted'
oauth_secret = 'redacted'

app = Flask(__name__)

t = Twitter(auth=OAuth(oauth_token, oauth_secret, CONSUMER_KEY, CONSUMER_SECRET))

@app.route("/", methods=['GET'])
def index():
	incidents = []
	tweets = t.statuses.user_timeline(screen_name='OPP_GTATraffic')
	tweets = tweets[:-10]
	for tweet in tweets:
		if findall('MVC|collision', tweet['text']) != []:
			incidents.append(parser.parse(tweet['created_at']))
	init_delta = datetime.now(pytz.utc) - incidents[0]
	total_time = init_delta.seconds
	total_incidents = len(incidents)
	for i in range(0, len(incidents)-1):
		diff = incidents[i] - incidents[i+1]
		total_time += diff.seconds
	average_time = total_time/total_incidents
	status = 1 # default: interval > 10 mins = low threat
	if average_time <= 180: # interval <= 3 mins = severe
		status = 3
	elif average_time > 180 and average_time <= 600: # interval 3 < x < 10 = moderate
		status = 2
	stylecss = url_for("static", filename="css/style.css")
	return render_template("index.html", status=status, stylecss=stylecss)

if __name__ == '__main__':
	app.run(debug=True)

