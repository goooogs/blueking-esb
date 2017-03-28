# -*- coding: utf-8 -*-
"""
Author: 唐 一
"""
import urllib2
import lxml.html, re
import logging

logger = logging.getLogger("api")

'''
从指定 url 抓取 html 源码
'''
def scratch(url):
    try:
        html = urllib2.urlopen(url).read()
    except urllib2.URLError as e:
        print 'Download error:', e.reason
        html = None
        logger.error("URL: %s" % url)
        raise
    return html


'''
解析HTML源码中的关键数据，默认只处理前100条
'''
def html_dump2list(html, record_count=100):
    result = []
    count = 0

    if not html:
        return {
            'result': False,
            'message': u'argument is None: html',
        }
    
    elements = lxml.html.fromstring(html)
    dictItems = [ i for i in elements.cssselect('div.tab-panel > div > div.explore-feed') if i is not None ]
    for i in dictItems:
        title = i.cssselect('h2 > a')[0].text_content().strip()  # 标题
        vote_count = i.cssselect('a.zm-item-vote-count')[0].text_content().strip()  # 票数
        author = i.cssselect('a.author-link')[0].text_content().strip() if len(i.cssselect('a.author-link')) > 0 else ""  # 回帖人
        bio = i.cssselect('span.bio')[0].text_content().strip() if len(i.cssselect('span.bio')) > 0 else "" # 回帖人说明
        if len(i.cssselect('a.toggle-expand')) > 0:
            i.cssselect('a.toggle-expand')[0].drop_tree()  # 移除summary中的'显示全部'
        summary = i.cssselect('div.zh-summary')[0].text_content().strip()
        href = i.cssselect('link[itemprop=url]')[0].get('href')
        m = re.search('/question/(\d+)/answer/(\d+)', href)
        if m and len(m.groups()) == 2:
            question_id = m.group(1)
            answer_id = m.group(2)
        else:
            continue
        result.append({
            'question_id': question_id,
            'title': title,
            'answer_id': answer_id,
            'vote_count': vote_count,
            'author': author,
            'bio': bio,
            'summary': summary,
            'href': href,
        })

        count = count + 1
        if count >= record_count:
            break

    return result


'''
获取知乎热帖列表，默认抓取前100条
'''
def get_daily_hot_list(url='https://www.zhihu.com/explore', record_count=100):
    html = scratch(url)
    result = html_dump2list(html, record_count)

    response = {}
    if result:
        response['result'] = True
        response['data'] = result
        response['message'] = u"第三方接口请求正常"
    else:
        response['result'] = False
        response['data'] = {}
        response['message'] = u"第三方接口请求异常"

    return response
