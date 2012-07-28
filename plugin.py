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
    
    def medals(self, irc, msg, args):
        """Display current medal count for the olympics."""
        
        url = self._b64decode('aHR0cDovL2VzcG4uZ28uY29tL29seW1waWNzL3N1bW1lci8yMDEyL21lZGFscw==')
        
        try:
            req = urllib2.Request(url)
            html = (urllib2.urlopen(req)).read()
        except:
            irc.reply("Failed to open: %s" % url)
            return
            
        soup = BeautifulSoup(html)
        h1 = soup.find('h1')

        div = soup.find('div', attrs={'class':'mt-overall'}) 
        bars = div.findAll('ul', attrs={'class':'medal-bar', 'style':'width:583px;'})

        object_list = []

        for bar in bars:
            country = bar.find('li', attrs={'class':'country'}).find('a')
            gold = bar.find('li', attrs={'class':'count-g'})
            silver = bar.find('li', attrs={'class':'count-s'})
            bronze = bar.find('li', attrs={'class':'count-b'})
            total = bar.find('li', attrs={'class':'total'})
            
            # for once, bspn has a garbage table. we compensate here. 
            if country is not None and gold is not None and silver is not None and bronze is not None and total is not None:
                d = collections.OrderedDict()
                d['country'] = country.renderContents().strip()
                d['gold'] = gold.renderContents().strip()
                d['silver'] = silver.renderContents().strip()
                d['bronze'] = bronze.renderContents().strip()
                d['total'] = total.renderContents().strip()
                object_list.append(d)

        # red title/top
        irc.reply(ircutils.mircColor("2012 London Summer Olympics Medal Tracker", 'red'))

        # header for table
        output = "{0:15} {1:5} {2:5} {3:5} {4:7}".format('Country', 'G', 'S', 'B', ircutils.bold('Total'))
        irc.reply(output)

        # iterate over the top5
        for each in object_list[0:6]:
            output = "{0:15} {1:5} {2:5} {3:5} {4:7}".format(each['country'], each['gold'], each['silver'], each['bronze'], ircutils.bold(each['total']))
            irc.reply(output)
    
    medals = wrap(medals)

Class = Olympics


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=250:
