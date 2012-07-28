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
    
    def _b64decode(self, string):
        """Returns base64 encoded string."""
        import base64
        return base64.b64decode(string)
    
    def medals(self, irc, msg, args, optlist, optcountry):
        """<mens|womens> <country>
        Display current medal count for the olympics. Use --mens or --womens to display totals via gender. Specify optional country to only display that country.
        """
 
        url = None
               
        if optlist:
            for (key, value) in optlist:
                if key == 'mens':
                    header = ircutils.mircColor("2012 London Summer Olympics Medal Tracker (Mens)", 'red')
                    url = 'http://www.nbcolympics.com/medals/library/2012-standings/tabs/medals/_men.html'
                if key == 'womens':
                    header = ircutils.mircColor("2012 London Summer Olympics Medal Tracker (Mens)", 'red')
                    url = 'http://www.nbcolympics.com/medals/library/2012-standings/tabs/medals/_women.html'
        
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
                
        # cheap way of only showing what someone searches for.
        if optcountry: 
            for each in object_list:
                if each['country'].startswith(optcountry):
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
        for each in object_list[0:3]:
            output = "{0:20} {1:5} {2:5} {3:5} {4:7}".format(each['country'], each['gold'], each['silver'], each['bronze'], ircutils.bold(each['total']))
            irc.reply(output)
    
    medals = wrap(medals, [getopts({'mens':'','womens':''}), optional('text')])

Class = Olympics


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=250:
