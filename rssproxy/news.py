# -*- encoding: utf-8 -*-

from django.contrib.syndication.feeds import Feed
from django.utils.feedgenerator import Atom1Feed
from django.shortcuts import render_to_response
from datetime import datetime

static_news = [
    {'pubdate': datetime(2010, 1, 10),
     'title': u'Κ',
     'description': """
     <p>Вчера в 6 утра по Москве служба технической поддержки ЖЖ
     наконец-таки ответила на письмо, которое я отправлял в конце
     сентября.</p>
     <blockquote><tt>
     Below is an answer to your support question regarding "[bot]
     rss-proxy.darkk.net.ru bot policy violation"
     (http://www.livejournal.com/support/see_request.bml?id=1009080&amp;auth=bqmv).<br/>

     ======================================================================<br/>

     I am sorry for the delay in responding.  Your RSS proxy is a
     violation of our Terms of Service because you are reproducing a
     feature only available to paid account members.  For that reason,
     we will not be removing this ban.<br/>

     Did this answer your question?<br/>
     YES:<br/>
     http://www.livejournal.com/support/act.bml?close;1009080;bqmvzh9x2a5kgj8;3965920<br/>
     NO:<br/>
     http://www.livejournal.com/support/see_request.bml?id=1009080&amp;auth=bqmv<br/>

     If you are having problems using any of the links in this email,
     please try copying and pasting the *entire* link into your
     browser's address bar rather than clicking on it.
     </tt></blockquote>

     <p>Забавно то, что ответ пришёл через 3½ месяца, забавно то, что я
     не могу закрыть тикет, кликнув по ссылке, т.к. у меня «нет прав»,
     забавно то, что в
     <a href="http://www.livejournal.com/support/faqbrowse.bml?faqid=131&amp;view=full">списке
     возможностей платного аккаунта</a> нет ни одного релевантного слова
     про RSS, а ленту друзей в RSS можно получить только через
     хитрозакрученные манипуляции со стилями (см. <a
     href="http://www.livejournal.com/support/faqbrowse.bml?faqid=149">FAQ
     №149</a>). Но не очень забавно то, что <em>формально</em> rss-proxy
     можно притянуть за уши к 19-му пункту XVI части
     <a href="http://www.livejournal.com/legal/tos-russian-translation.bml">ToS</a>.
     </p>

     <p>
     Кстати, <a href="http://blog.swined.net/">swined</a>, автора <a
     href="http://lj2rss.net.ru">lj2rss</a>, тоже из SUP подобными
     фразами <a href="http://blog.swined.net/2009/12/blog-post.html">стращали</a>.
     Интересно, чем всё закончилось?
     </p>
     """},

    {'pubdate': datetime(2009, 12, 29),
     'title': u'Ι',
     'description': """
     <p>Да, кстати, для истории стоит отметить, что 10-го декабря rss-proxy был
     вынесен из бан-листа, после чего через 12 часов работы был
     <a href="http://twitter.com/mathemonkey/status/6526055725">забанен опять</a> и
     <a href="http://twitter.com/mathemonkey/status/6692647251">возобновил
     работу 15-го декабря</a>. Две недели — полёт нормальный!</p>
     """},

    {'pubdate': datetime(2009, 12, 6),
     'title': u'θ',
     'description': """
     <p>Новости не особо оригинальные и на этот раз — с 23-го ноября rss-proxy
     снова <a href="http://twitter.com/mathemonkey/status/5952773825">забанен</a>
     и на настоящий момент бан не снят.</p>

     <p>Но на этот раз новостей несколько больше. После моего обращения в сообщество
     <a class="ljcomm" href="http://community.livejournal.com/lj_ru_support/">lj_ru_support</a>
     с вопросом: «А какой-же пункт policy я нарушаю?» — мне
     <a href="http://twitter.com/mathemonkey/status/6058302214">порекомендовали</a>
     обратиться к главному инженеру компании — Илье Дронову
     (<a href="http://igrick.livejournal.com" class="ljuser">igrick</a>),
     с которым я с 26-го ноября и веду неторопливую переписку по вопросам «кто
     виноват?» и «что делать?».</p>

     <p>Stay tuned!</p>
     """},

    {'pubdate': datetime(2009, 11, 15),
     'title': u'η',
     'description': """
     <p>И снова суп забанил rss-proxy, и снова нет комментариев
     webmaster@livejournal.com, и снова другой User-Agent, и всё вернулось на
     круги своя.</p>
     """},

    {'pubdate': datetime(2009, 10, 27),
     'title': u'ζ',
     'description': """
     <p>Т.к. в течение недели ответа от webmaster@livejournal.com получено не
     было, у бота был сменён User-Agent с
     <q><code>Rss-Proxy (http://rss-proxy.darkk.net.ru;
     leon+rss-proxy@darkk.net.ru) AppEngine-Google;
     (+http://code.google.com/appengine; appid rss-proxy)</code></q>
     на
     <q><code>Rss-Proxy (http://RSS-PROXY.DARKK.NET.RU;
     leon+rss-proxy@DARKK.NET.RU) AppEngine-Google;
     (+http://code.google.com/appengine; appid rss-proxy)</code></q>
     .</p>

     <p>Объявляется конкурс на лучший User-Agent, который соответствует
     <a href="http://www.livejournal.com/bots/">правилам Живого Журнала для
     роботов</a>. Жду ваши вариации на
     <a href="mailto:leon+rss-proxy&#64;darkk.net.ru">почту</a> или в твиттер <a
     href="http://twitter.com/mathemonkey">@mathemonkey</a>.</p>
     """},

    {'pubdate': datetime(2009, 10, 22),
     'title': u'ε',
     'description': """
     <p>В ночь с 20-го на 21-е октября без объявления войны rss-proxy был
     вероломно забанен LiveJournal со следующей формулировкой:</p>
     <blockquote><p>
         Your RSS Aggregation Service violates our Acceptable Usage Policy.
     </p></blockquote>

     <p>Комментариев со стороны webmaster@livejournal.com в течение полутора
     суток так и не поступило.</p>
     """},

    {'pubdate': datetime(2009, 6, 26),
     'title': u'δ',
     'description': """
     <p>В связи с возросшей нагрузкой на сервис проведены некоторые
     оптимизации. В некоторых случаях бот GoogleReader не сообщает число
     подписчиков фида, предположительно, в этих случаях число подписчиков
     строго равно нулю и, соответственно, боту можно отдать пустой фид.</p>

     <p>До оптимизации сервис исползовал ~95% квоты бесплатного трафика
     в день.</p>
     """},

    {'pubdate': datetime(2009, 2, 8),
     'title': u'γ',
     'description': """
     <p>Исправлено несколько недочётов:</p>

     <ul>
     <li>Google Chrome теперь нормально скачивает OPML-файл.</li>
     <li>Пользователи с большим числом друзей уже тоже могут получить
     свой OPML-файл без каких-либо проблем.</li>
     <li>Исправлена проблема с кривыми кодировками в LJ, т.к. LJ не
     всегда отдаёт данные в корректной UTF-8.</li>
     </ul>

     <p>Также, при генерации нового OPML файла в имя потока добавляется
     LJ-имя специально для того, чтоб визуально отличать
     <a class="ljcomm"
     href="http://community.livejournal.com/ru_root">ru_root</a> от
     <a class="ljcomm"
     href="http://community.livejournal.com/ru_sysadmins">ru_sysadmins</a>
     и прочие <em>с виду</em> родственные сообщества.</p>
     """},

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
        return static_news[:5]

def sitenews(req):
    return render_to_response('sitenews.html', {'news': static_news})
