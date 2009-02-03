# -*- encoding: utf-8 -*-

from django.contrib.syndication.feeds import Feed
from django.utils.feedgenerator import Atom1Feed
from django.shortcuts import render_to_response
from datetime import datetime

static_news = [
    {'pubdate': datetime(2009, 01, 31),
     'title': u'β',
     'description': """
     <p>Сервис обзавёлся дизайном, <a href="/faq">FAQ</a>, возможностью
     обрезать контент «подзамочных» записей и был открыт в публичное
     бета-тестирование на хабрахабре.</p>

     <p>В тот же день десяток бравых тестеров нашли следующие баги... в
     ЖЖ :-)</p>

     <ul>
     <li>Если во френдленте есть RSS-трансляции, то ЖЖ с вероятностью
     порядка 50% отдаёт некорректный XML, который сервис не может
     воспринять.</li>
     <li>У некоторых LJ-пользователей списки LJ-друзей в «fdata» и «FOAF»
     не согласованы, что приводит к проблемам при отображении списка
     LJ-друзей перед последующей генерацией OPML-файла.</li>
     </ul>

     <p>По мере создания разных обходных путей решения этих проблем
     будут появляться дальнейшие новости. Поддержка групп LJ-друзей будет
     добавлена «как только так сразу», если, конечно,
     <a href="http://www.livejournal.com/doc/server/ljp.csp.xml-rpc.getfriendgroups.html">
     документация от LiveJournal.com</a> соответствует действительности.
     </p>
     """},

    {'pubdate': datetime(2009, 01, 06),
     'title': u'α',
     'description': """
     <p>В мир была выпущена первая альфа-версия сервиса, абсолютно без
     интерфейса и документации, но уже вполне работоспособная.</p>
     """},
]

class SiteNews(Feed):
    feed_type = Atom1Feed
    title = 'Новости сервиса rss-proxy.darkk.net.ru'
    link = '/sitenews'

    def item_link(self, item):
        return self.link + '#' + item['pubdate'].strftime('%Y%m%d')

    def item_pubdate(self, item):
        return item['pubdate']

    def items(self):
        return static_news

def sitenews(req):
    return render_to_response('sitenews.html', {'news': static_news})
