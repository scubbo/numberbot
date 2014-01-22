#!/usr/bin/python
'''
Dependencies:
* pattern
* python-twitter
'''
import twitter
import os, os.path
import sys
import urllib2
import re
import time
from pattern.en import number as numberParse

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + os.path.sep + os.path.pardir + os.path.sep + 'twitterbot')
import tb

os.chdir(os.path.dirname(os.path.abspath(__file__)))

class App:
	def __init__(self, twitterBot = None):
		'''gens is a dictionary of {name:instance of phraseGenerator}'''
		self.twitterBot = twitterBot
		self.interestWords = ['interesting', 'trivia', 'fact']
	
	def postUpdate(self):
		numberfact = self.randomfact()
		while len(numberfact) > 140:
			numberfact = self.randomfact()
		self.twitterBot.api.PostUpdate(numberfact)
		print 'numberbot posted ' + numberfact

	def postUpdateTest(self):
		numberfact = self.randomfact()
		while len(numberfact) > 140:
			numberfact = self.randomfact()
		print 'numberbot test-posted ' + numberfact
	
	def postReply(self, mention):
		recip = mention.user.screen_name
		if recip != "I_Like_Numbers":
			theNumber = self.findNumber(mention.text)
			if type(theNumber) == type(1):
				numberfact = self.numberfact(theNumber)
				while len(numberfact) > 138 - len(recip):
					numberfact = self.numberfact(theNumber)
				self.twitterBot.api.PostUpdate('@' + recip + ' ' + numberfact)
				print '\n' + time.asctime() + ' In reply to ' + mention.text + '\n\tPosted ' + numberfact
			else:
				if theNumber == 'random':
					randomfact = self.randomfact()
					while len(randomfact) > 138 - len(recip):
						randomfact = self.randomfact()
					self.twitterBot.api.PostUpdate('@' + recip + ' ' + randomfact)
					print '\n' + time.asctime() + ' In reply to ' + mention.text + '\n\tPosted randomfact ' + randomfact
				else:
					print 'Didn\'t do anything'
	
	def findNumber(self, text):
		prospectiveNumber = numberParse(text)
		if prospectiveNumber != 0:
			return prospectiveNumber
		comp = re.compile('[.,?!]')
		subbed = comp.sub(' ', text)
		if numberParse(subbed) != 0:
			return numberParse(subbed)
		if text.find('0') > -1 or text.find('zero') > -1 or text.find('nought') > -1:
			return 0
		if text.find('random') > -1:
			return 'random'
		return False
	
	def replyMentions(self):
		if os.path.exists('lastMention.file'):
			with file('lastMention.file', 'r') as f:
				lastMention = int(f.read())
				mentions = self.twitterBot.api.GetMentions(since_id=lastMention)
		else:
			mentions = self.twitterBot.api.GetMentions()
		if len(mentions) > 0:
			with file('lastMention.file', 'w') as f:
				f.write(str(mentions[0].id))
		for mention in mentions:
			print '\nDealing with ' + mention.text + ' from ' + mention.user.screen_name
			self.postReply(mention)
	
	def makeFriends(self):
		#First, befriend anyone you haven't already
		newFriends = [newFriend.screen_name for newFriend in self.twitterBot.api.GetFollowers() if newFriend not in self.twitterBot.api.GetFriends()]
		for newFriend in newFriends:
			try:
				self.twitterBot.api.CreateFriendship(newFriend)
				print '\nFollowed ' + newFriend
			except:
				print 'Tried to follow ' + newFriend + ', but there was an error. Perhaps they have a hidden profile?'
				
	def scanFriendTweets(self):
		if os.path.exists('lastSearch.file'):
			with file('lastSearch.file', 'r') as f:
				lastSearch = int(f.read())
		else:
			lastSearch = 0
		
		tweets = self.twitterBot.api.GetUserTimeline(since_id=lastSearch)
		
		for tweet in tweets:
			if self.findNumber(tweet.text) != False and self.findNumber(tweet.text) > 4 and reduce(lambda x, y: x or y, [word in tweet.text for word in self.interestWords]):
				self.postReply(tweet)
		
		ids = [tweet.id for tweet in tweets]
		ids.sort()
		
		if len(ids) > 0:
			with file('lastSearch.record', 'w') as f:
				f.write(str(ids[-1]))
			
	
	def numberfact(self, number):
		return unicode(urllib2.urlopen('http://numbersapi.com/' + str(number)).read().decode('utf-8'))
	
	def randomfact(self):
		return unicode(urllib2.urlopen('http://numbersapi.com/random').read().decode('utf-8'))
		

if __name__ == '__main__':
	theTB = tb.Twitterbot('DDXKzIk54aVhnreJs9haIw', 'dANALAJBcLjTQ9xh2IGg0o44RXM9meLwzEg9JhUU')
	theApp = App(theTB)
	if len(sys.argv) == 1:
		raise IOError('You need to provide \'post\' or \'listen\' as an argument to this script!')
	if sys.argv[1] == 'post':
		theApp.postUpdate()
	if sys.argv[1] == 'listen':
		theApp.replyMentions()
		#theApp.scanFriendTweets()
	if sys.argv[1] == 'makeFriends':
		theApp.makeFriends()
	if sys.argv[1] == 'postTest':
		theApp.postUpdateTest()
