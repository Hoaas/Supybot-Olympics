###
# Copyright (c) 2012, spline
# All rights reserved.
#
#
###

from BeautifulSoup import BeautifulSoup
import urllib2
import re
import collections
import datetime
import time
import string

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
from supybot.i18n import PluginInternationalization, internationalizeDocstring

_ = PluginInternationalization('Olympics')

@internationalizeDocstring
class Olympics(callbacks.Plugin):
    """Add the help for "@plugin help Olympics" here
    This should describe *how* to use this plugin."""
    threaded = True
    
    def olympicscores(self, irc, msg, args, optsport):
        """[sport]
        Display scores for various Olympic Sports. Sport must be one of: menssoccer, womenssoccer, mensbb, womensbb
        """
        
        # needs some optdate handling. 
    
        validsports = {'menssoccer':'188', 'womenssoccer':'364', 'mensbb':'223', 'womensbb':'345'}
    
        if optsport not in validsports:
            irc.reply("Invalid sport. Must be one of: %s" % validsports.keys())
            return
    
        url = 'http://m.espn.go.com/extra/olympics/scoreboard'
        #url += '?date=%s' % datetime.datetime.now().strftime("%Y%m%d")
        url += '?eventId=%s&wjb=' % validsports[optsport]

        try:
            req = urllib2.Request(url)
            html = (urllib2.urlopen(req)).read()
        except:
            irc.reply("Failed to open: %s" % url)
            return
            
        
        soup = BeautifulSoup(html)
        #eventdate = soup.find('div', attrs={'class':'sub dark'}).text
        #eventdate = eventdate.split('|') # cheap way to get date.
        table = soup.find('table', attrs={'class':'wide'})
        rows = table.findAll('tr')

        append_list = []

        for row in rows:
            event = row.find('td').text
            append_list.append(event)
    
        output = string.join([item for item in append_list], " | ")
    
        irc.reply(output)
        #irc.reply(ircutils.mircColor(eventdate[0].strip(), 'red') + " :: " + output)
    
    olympicscores = wrap(olympicscores, [('somethingWithoutSpaces')])
    
    
    def olympicevents(self, irc, msg, args, optsport):
        """[sport]
        Show olympic events in sport for date.
        """
        
        sportstable = {'soccer':'19', 'basketball':'7', 'volleyball':'46', 'diving':'16'}
        
        if optsport not in sportstable:
            irc.reply("Invalid sport. Must be one of: %s" % sportstable.keys())
            return
                
        today = datetime.datetime.now().strftime("%A, %B %d")
        
        url = 'http://espn.go.com/olympics/summer/2012/schedule/_/sport/%s' % sportstable[optsport]
        
        try:
            req = urllib2.Request(url)
            html = (urllib2.urlopen(req)).read()
        except:
            irc.reply("Failed to open: %s" % url)
            return
            
        html = html.replace('class="evenrow"', 'class="oddrow"')

        soup = BeautifulSoup(html)
        table = soup.find('table', attrs={'class':'tablehead'}) 

        rows = table.findAll('tr', attrs={'class':'oddrow'})

        object_list = []
        
        for row in rows:
            time = row.find('td')
            date = row.findPrevious('tr', attrs={'class':'stathead'}).find('td', attrs={'colspan':'4'})
            event = time.findNext('td').findNext('td')
            d = collections.OrderedDict()
            d['date'] = date.renderContents().strip()
            d['time'] = time.renderContents().strip()
            d['event'] = event.renderContents().strip()
            object_list.append(d)
            
        if len(object_list) > 0:
            header = "Olympic Events Today for %s :: (All times ET)" % optsport.title()
            irc.reply(ircutils.mircColor(header,'red'))
            
            for each in object_list: # fast, not clean. Needs events of the day, etc.
                if each['date'] == today:
                    irc.reply("{0:10} {1:100}".format(each['time'], each['event']))
        else:
            irc.reply("No events scheduled for today.")
    
    olympicevents = wrap(olympicevents, [('somethingWithoutSpaces')])

    def olympicbbgroups(self, irc, msg, args, optgender, optgroup):
        """[mens|womens] [groupa|groupb]
        Display Olympic Basketball Group Standings. Must supply gender (mens|womens) and (groupa|groupb)
        """

        optgender = optgender.lower().strip()
        
        if optgender != "mens" and optgender != "womens":
            irc.reply("Gender must be: mens or womens")
            return
        
        optgroup = optgroup.lower().strip()
        
        if optgroup != "groupa" and optgroup != "groupb":
            irc.reply("Group must be: groupa or groupb")
            return
        
        if optgender == "mens":
                url = 'http://www.nbcolympics.com/sports/sport=basketball/library/home/_groups_men.html'
        else:
                url = 'http://www.nbcolympics.com/sports/sport=basketball/library/home/_groups_women.html'

        self.log.info(url)
        self.log.info(optgroup)
        
        try:
            req = urllib2.Request(url)
            html = (urllib2.urlopen(req)).read()
        except:
            irc.reply("Failed to load: %s" % url)
            return
            
        soup = BeautifulSoup(html)
        
        if optgroup == "groupa":
            group = soup.find('div', attrs={'class':'or-groupL'})
        else:
            group = soup.find('div', attrs={'class':'or-groupR'})
            
        tbody = group.find('tbody')
        rows = tbody.findAll('tr')

        irc.reply("{0:5} {1:7} {2:4} {3:4}".format("RK", "TEAM", "GP", "PTS"))

        for row in rows:
            rank = row.find('td', attrs={'class':'or-c'})
            country = rank.findNext('span', attrs={'class':'or-flag'}).find('img')['alt']
            gp = rank.findNext('td', attrs={'class':'or-c'})
            pts = gp.findNext('td', attrs={'class':'or-c or-hl'})
            irc.reply("{0:5} {1:10} {2:4} {3:4}".format(rank.text, ircutils.bold(country), gp.text, pts.text))
    
    olympicbbgroups = wrap(olympicbbgroups, [('somethingWithoutSpaces'), ('somethingWithoutSpaces')])    

    
    def medals(self, irc, msg, args, optlist, optcountry):
        """[--mens | --womens] [--num <value>] [<country>]
        Display current medal count for the olympics. Use --mens or --womens to display totals via gender. Specify optional country to only display that country.
        """
 
        url = None
        num = 3
        if optlist:
            for (key, value) in optlist:
                if key == 'mens':
                    header = ircutils.mircColor("2012 London Summer Olympics Medal Tracker (Mens)", 'red')
                    url = 'http://www.nbcolympics.com/medals/library/2012-standings/tabs/medals/_men.html'
                if key == 'womens':
                    header = ircutils.mircColor("2012 London Summer Olympics Medal Tracker (Womens)", 'red')
                    url = 'http://www.nbcolympics.com/medals/library/2012-standings/tabs/medals/_women.html'
                if key == 'num':
                    if value < 1:
                        num = 1
                    elif value > 10:
                        irc.reply('Please. Max 10.')
                        return
                    else:
                        num = value
        
        if not url: # default to all
            header = ircutils.mircColor("2012 London Summer Olympics Medal Tracker", 'red')
            url = 'http://www.nbcolympics.com/medals/library/2012-standings/tabs/medals/_overall.html'
        
        try:
            req = urllib2.Request(url)
            html = (urllib2.urlopen(req)).read()
        except:
            irc.reply("Failed to open: %s" % url)
            return
            
        soup = BeautifulSoup(html)
        tbody = soup.find('tbody')
        rows = tbody.findAll('tr', attrs={'class':re.compile('^or.*?')})

        object_list = []

        for row in rows:
            country = row.find('div', attrs={'class':'or-country'}).find('img')['title']
            gold = row.find('td', attrs={'class':'or-gold or-c'})
            silver = row.find('td', attrs={'class':'or-silver or-c'})
            bronze = row.find('td', attrs={'class':'or-bronze or-c'})
            total = row.find('td', attrs={'class':'or-total or-c'})
            
            d = collections.OrderedDict()
            d['country'] = country
            d['gold'] = gold.renderContents().strip()
            d['silver'] = silver.renderContents().strip()
            d['bronze'] = bronze.renderContents().strip()
            d['total'] = total.renderContents().strip()
            object_list.append(d)

        if self.registryValue('sortByGold', msg.args[0]):
            bronze = lambda x: int(x.get('bronze'))
            object_list = sorted(object_list, key=bronze, reverse=True)

            silver = lambda x: int(x.get('silver'))
            object_list = sorted(object_list, key=silver, reverse=True)

            gold = lambda x: int(x.get('gold'))
            object_list = sorted(object_list, key=gold, reverse=True)

        # cheap way of only showing what someone searches for.
        if optcountry: 
            for each in object_list:
                if each['country'].lower().startswith(optcountry.lower()):
                    output = "{0:20} G: {1:5} S: {2:5} B: {3:5} T: {4:7}".format(ircutils.underline(each['country']),\
                        ircutils.bold(each['gold']), ircutils.bold(each['silver']), ircutils.bold(each['bronze']), ircutils.bold(ircutils.bold(each['total'])))
                    irc.reply(output)
            return

                 
        # red title/top
        irc.reply(header)

        # header for table
        output = "{0:20} {1:5} {2:5} {3:5} {4:7}".format('Country', 'G', 'S', 'B', ircutils.bold('Total'))
        irc.reply(output)

        # iterate over the top3
        for each in object_list[0:num]:
            output = "{0:20} {1:5} {2:5} {3:5} {4:7}".format(each['country'], each['gold'], each['silver'], each['bronze'], ircutils.bold(each['total']))
            irc.reply(output)
    
    medals = wrap(medals, [getopts({'mens':'','womens':'','num':('int')}), optional('text')])

Class = Olympics


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=250:
