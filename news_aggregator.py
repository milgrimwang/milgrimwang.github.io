#!/usr/bin/env python
"""
RSS feeds news aggregator
"""
import re
import os
import urllib.request
from urllib.parse import urlparse
from datetime import datetime, timedelta, timezone

from lxml import html
from jinja2 import Environment, FileSystemLoader

RSS_FEEDS = [
    "https://www.technologyreview.com/feed/",
    "https://www.eurogamer.net/feed",
    "https://feeds.arstechnica.com/arstechnica/index",
    "https://www.engadget.com/rss.xml",
    "https://techcrunch.com/feed/",
    "https://www.bleepingcomputer.com/feed/",
    "https://www.theregister.com/headlines.atom",
    "https://spectrum.ieee.org/customfeeds/feed/all-topics/rss",
    "https://www.science.org/rss/news_current.xml",
    "https://www.securityweek.com/feed",
]
NEWS_URLS = [
    "https://lobste.rs/",
    "https://news.ycombinator.com/",
]
DT_FORMAT = [
    "%a, %d %b %Y %H:%M:%S %z",
    "%Y-%m-%dT%H:%M:%S%z",
    "%a, %d %b %y %H:%M:%S %z",
    "%Y-%m-%dT%H:%M:%S.%fZ",
    "%Y-%m-%d %H:%M:%S",  # Lobsters
    "%Y-%m-%dT%H:%M:%S",  # HN
]
TPL_FORMAT = "%a, %d %b %Y %H:%M:%S"
INTERVAL = datetime.now(timezone.utc) - timedelta(hours=12)
TITLE = "News aggregator"
TEMPLATE_FILE = "index.tpl"
SKIP_NEWS = [
    "Today's NYT",
    "Quordle today",
    "NYT Strands today",
    "Today's Wordle Hints",
    "NYT Connections today",
    "Best Internet Providers",
    "Livestream: How to Watch",
    "How to Watch",
    "Best Places to Buy",
    "Exclusive deal:",
    "Best VPN",
    "Climate Tech Companies to Watch",
    "TechCrunch Disrupt",
    "Prime Day",
    "The Morning After",
    "Black Friday",
    "Cyber Monday",
    "The best",
    "deals",
    "release date",
    "hints and answers",
    "episode",
    "free movies",
]
SKIP_DOMAINS = [
    "bbc.com",
]


def get_url_content(url):
    print(f"Download {url}")
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

    if "EST" in dt_string:
        dt_string = dt_string.replace("EST", "-05:00")

    for dt_format in DT_FORMAT:
        try:
            return datetime.strptime(dt_string, dt_format).replace(tzinfo=timezone.utc)
        except ValueError:
            pass

    raise ValueError(f"Failed to parse {dt_string}")


def first_or_none(values):
    return values[0].strip() if values else None


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
                if "&amp;" in title:
                    title = title.replace("&amp;", "&")

                if any(skip.lower() in title.lower() for skip in SKIP_NEWS):
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
                domain = urlparse(rss_url).netloc.replace("www.", "").replace("feeds.", "").replace("spectrum.", "")
                news_links.append({
                    "url": news_url, "text": title, "time": created_at.strftime(TPL_FORMAT), "ts": created_at, "domain": domain,
                })

    for news_url in NEWS_URLS:
        news_content = get_url_content(news_url)
        if news_content is None:
            print(f"No news content for {news_url}")
            continue

        x = html.fromstring(news_content)
        # Lobsters
        details = x.xpath('//div[@class="details"]')
        if details:
            for detail in details:
                url = first_or_none(detail.xpath('.//a[@class="u-url"]/@href'))
                if url and not url.startswith("https"):
                    continue
                if any(domain in url for domain in SKIP_DOMAINS):
                    continue
                title = first_or_none(detail.xpath('.//a[@class="u-url"]/text()'))
                created_at = parse_dt_string(first_or_none(detail.xpath(".//time/@title")))

                domain = urlparse(url).netloc.replace("www.", "").replace("feeds.", "").replace("spectrum.", "")
                news_links.append({
                    "url": url, "text": title, "time": created_at.strftime(TPL_FORMAT), "ts": created_at, "domain": domain,
                })
    
            continue

        # HN
        details = x.xpath('//tr[@class="athing submission"]')
        if details:
            for detail in details:
                url = first_or_none(detail.xpath('.//span[@class="titleline"]/a/@href'))
                if url and not url.startswith("https"):
                    continue
                if any(domain in url for domain in SKIP_DOMAINS):
                    continue
                title = first_or_none(detail.xpath('.//span[@class="titleline"]/a/text()'))
                created_at = parse_dt_string(first_or_none(detail.xpath('..//tr//span[@class="age"]/@title')))


                domain = urlparse(url).netloc.replace("www.", "").replace("feeds.", "").replace("spectrum.", "")
                news_links.append({
                    "url": url, "text": title, "time": created_at.strftime(TPL_FORMAT), "ts": created_at, "domain": domain,
                })

            continue

    
    if news_links:
        news_links = sorted(news_links, key=lambda link: link["ts"], reverse=True)
        env = Environment(loader=FileSystemLoader("."))
        template = env.get_template(TEMPLATE_FILE)
        updated_at = datetime.now(timezone.utc).strftime(TPL_FORMAT)
        with open("index.html", "w") as index_file:
            index_file.write(template.render(title=TITLE, links=news_links, updated_at=updated_at))


if __name__ == "__main__":
    main()
