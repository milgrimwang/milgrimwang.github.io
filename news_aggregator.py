#!/usr/bin/env python
"""
RSS feeds news aggregator
"""
import re
import os
import urllib.request
from urllib.parse import urlparse
from datetime import datetime, timedelta, timezone


from jinja2 import Environment, FileSystemLoader

RSS_FEEDS = [
    "https://www.technologyreview.com/feed/",
    "https://www.eurogamer.net/feed",
    "https://www.cnet.com/rss/news/",
    "https://gizmodo.com/feed",
    "https://www.techradar.com/feeds/articletype/news",
    "https://feeds.arstechnica.com/arstechnica/index",
    "https://www.engadget.com/rss.xml",
    "https://www.theverge.com/rss/index.xml",
    "https://techcrunch.com/feed/",
    "https://www.bleepingcomputer.com/feed/",
    "https://www.cisa.gov/news.xml",
    "https://krebsonsecurity.com/feed/",
    "https://www.schneier.com/feed/atom/",
    "https://www.afcea.org/signal-articles-feed.xml",
    "https://phys.org/rss-feed/",
    "https://www.theregister.com/headlines.atom",
    "https://blog.torproject.org/feed",
    "https://lichess.org/@/Lichess/blog.atom",
]
DT_FORMAT = [
    "%a, %d %b %Y %H:%M:%S %z",
    "%Y-%m-%dT%H:%M:%S%z",
    "%a, %d %b %y %H:%M:%S %z",
    "%Y-%m-%dT%H:%M:%S.%fZ",
]
TPL_FORMAT = "%a, %d %b %Y %H:%M:%S"
INTERVAL = datetime.now(timezone.utc) - timedelta(hours=24)
TITLE = "News aggregator"
TEMPLATE_FILE = "index.tpl"
SKIP_NEWS = [
    "Today's NYT",
    "Today's Wordle Hints",
    "NYT Connections today",
    "Best Internet Providers",
]


def get_url_content(url):
    # print(f"Download {url}")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:130.0) Gecko/20100101 Firefox/130.0'
        }
        request = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(request) as response:
            return response.read().decode("utf-8")
    except Exception as ex:
        print(f"Failed to download {url} because of {ex}")


def parse_dt_string(dt_string):
    if "EDT" in dt_string:
        dt_string = dt_string.replace("EDT", "-04:00")

    for dt_format in DT_FORMAT:
        try:
            return datetime.strptime(dt_string, dt_format).replace(tzinfo=timezone.utc)
        except ValueError:
            pass

    raise ValueError(f"Failed to parse {dt_string}")


def main():
    news_links = []
    for rss_url in RSS_FEEDS:
        rss_content = get_url_content(rss_url)
        if rss_content is None:
            continue

        items = re.findall(r"<item>(.*?)</item>", rss_content, re.DOTALL)
        if not items:
            items = re.findall(r"<item rdf.*?>(.*?)</item>", rss_content, re.DOTALL)
        if not items:
            items = re.findall(r"<entry>(.*?)</entry>", rss_content, re.DOTALL)
        for item in items:
            title = re.findall(r"<title>(.*?)</title>", item, re.DOTALL)
            if not title:
                title = re.findall(r"<title.*?>(.*?)</title>", item, re.DOTALL)
            if title:
                title = title[0].strip()
                if "<![CDATA[" in title:
                    title = title.replace("<![CDATA[", "").replace("]]>", "").strip()
                if "&#8217;" in title:
                    title = title.replace("&#8217;", "'")
                if "&#039;" in title:
                    title = title.replace("&#039;", "'")
                if "&#8243;" in title:
                    title = title.replace("&#8243;", '"')

                if any(skip in title for skip in SKIP_NEWS):
                    continue

            news_url = re.findall(r"<link>(.*?)</link>", item, re.DOTALL)
            if not news_url:
                news_url = re.findall(r'<link.*?href="(.*?)"', item, re.DOTALL)
            if news_url:
                news_url = news_url[0].strip()
                if "<![CDATA[" in news_url:
                    news_url = news_url.replace("<![CDATA[", "").replace("]]>", "").strip()

            created_at = re.findall(r"<pubDate>(.*?)</pubDate>", item, re.DOTALL)
            if not created_at:
                created_at = re.findall(r"<dc:date>(.*?)</dc:date>", item, re.DOTALL)
            if not created_at:
                created_at = re.findall(r"<published>(.*?)</published>", item, re.DOTALL)
            if not created_at:
                created_at = re.findall(r"<updated>(.*?)</updated>", item, re.DOTALL)
            if created_at:
                created_at = created_at[0].strip()
                created_at = parse_dt_string(created_at)

            if created_at > INTERVAL:
                domain = urlparse(rss_url).netloc.replace("www.", "").replace("feeds.", "")
                news_links.append({
                    "url": news_url, "text": title, "time": created_at.strftime(TPL_FORMAT), "ts": created_at, "domain": domain,
                })

    if news_links:
        news_links = sorted(news_links, key=lambda link: link["ts"], reverse=True)
        env = Environment(loader=FileSystemLoader("."))
        template = env.get_template(TEMPLATE_FILE)
        updated_at = datetime.now(timezone.utc).strftime(TPL_FORMAT)
        with open("index.html", "w") as index_file:
            index_file.write(template.render(title=TITLE, links=news_links, updated_at=updated_at))


if __name__ == "__main__":
    main()
