import klout, time
from klout import Klout
from apscheduler.scheduler import Scheduler
from twilio.rest import TwilioRestClient
from twilio import twiml
sched = Scheduler()

klout_obj = Klout('nrcaux4yrmmgfwmn3cy2dmxm')

account = "ACe37ca473de62d8925f50d0280b10301a"
token = "b7295a0e4dd683cfa9138d47158c2522"
client = TwilioRestClient(account, token)

def sendMsg(msg, phone):
    client.sms.messages.create(to=phone, from_="+19018710695", body=msg)


success = False
while not success:
    twitter_sns = raw_input('What twitter names do you want to follow? ')
    twitter_sns = twitter_sns.split(', ')
    klout_ids = {}
    influencees = {}
    topics = {}
    for twitter_sn in twitter_sns:
        try:
            klout_id = klout_obj.identity.klout(screenName=twitter_sn).get('id')
            klout_ids[twitter_sn] = klout_id
            result = klout_obj.user.influence(kloutId=klout_id)
            influencees[twitter_sn] = []
            for item in result['myInfluencees']:
                influencees[twitter_sn] += item['entity']['payload']['nick']
            success = 1
        except klout.api.KloutHTTPError:
            print "Sorry, we couldn't find %s. We'll have to skip that one." \
                  % twitter_sn
            twitter_sns.remove(twitter_sn)

phone = raw_input("Cool. What number do you want to be notified on about changes? ")
msg = "Here's your initial notification.\n"
old_scores = {}
for sn in twitter_sns:
    score = klout_obj.user.score(kloutId=klout_ids[sn]).get('score') - 1
    old_scores[sn] = score
    msg += "%s - %i \n" % (sn, score)
sendMsg(msg, phone)

while True:
    time.sleep(20)
    msg = ""
    msg2 = ''
    changed_sn = ""
    send_text = False
    for sn in twitter_sns:
        score = klout_obj.user.score(kloutId=klout_ids[sn]).get('score')
        if score > old_scores[sn] + 0.0000001:
            changed_sn = sn
            msg = "Oh wow! %s just saw a change of %i points! " \
                  % (sn, score - old_scores[sn])
            msg += "I'd ask what to send next," \
                   "but since you're demoing, I'll just send it."
            send_text=True
            influencees[sn] = []
            if not msg2:
                msg2 = 'Follower changes today:\n'
                for item in result['myInfluencees'][:4]:
                    msg2 += item['entity']['payload']['nick'] + " = "
                    msg2 += "%.2f" % round(item['entity']['payload']['scoreDeltas']['dayChange'],2) +"\n"
        old_scores[sn] = score
    if send_text:
        sendMsg(msg, phone)
        sendMsg(msg2, phone)