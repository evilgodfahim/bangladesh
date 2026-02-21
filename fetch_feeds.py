# fetch_feeds_fixed.py
import feedparser
from datetime import datetime, timezone
import hashlib
import os
import re
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import concurrent.futures

# ---- CONFIG ----
TIMEOUT = 10                 # seconds per HTTP request
MAX_WORKERS = 12             # concurrent fetches
RETRIES = 2                  # per-request retries
BACKOFF_FACTOR = 0.5         # retry backoff
# Removed the problematic FT feed (https://www.ft.com/rss/world)
FEEDS = [
    "https://asiatimes.com/feed/",
    "https://politepaul.com/fd/TefnRxuxFzO0.xml",
    "https://evilgodfahim.github.io/gd/merged.xml",
    "https://www.dawn.com/feeds/latest-news/",
    "https://evilgodfahim.github.io/csis/rss.xml",
    "https://www.dawn.com/feeds/world/",
    "https://politepaul.com/fd/x2KIPhf4eLsZ.xml",
    "https://politepaul.com/fd/9RMAFvRRGLst.xml",
    "https://www.globalpolicyjournal.com/blog/author/%2A/feed",
    "https://www.e-ir.info/feed/",
    "https://www.theglobalist.com/feed/",
    "https://responsiblestatecraft.org/feed/",
    "https://politepaul.com/fd/ffERiOdKxWlq.xml",
    "https://politepaul.com/fd/dCWMZKe7BJqi.xml",
    "https://politepaul.com/fd/YJRa9YOT7CyB.xml",
    "https://meduza.io/rss/en/all",
    "https://politepaul.com/fd/JsMAwSx6Pkbr.xml",
    "https://evilgodfahim.github.io/alm/combined.xml",
    "https://evilgodfahim.github.io/start/combined.xml",
    "https://politepaul.com/fd/GbcosKoaAE22.xml",
    "https://www.noemamag.com/article-topic/geopolitics-globalization/feed/",
    "https://zeihan.com/feed/",
    "https://politepaul.com/fd/ELc5hcluIkDO.xml",
    "https://original.antiwar.com/feed/",
    "https://www.atlanticcouncil.org/feed/",
    "https://warontherocks.com/feed/",
    "https://www.thehindu.com/opinion/editorial/?service=rss",
    "https://politepaul.com/fd/aCEp2lWYu3Jn.xml",
    "https://evilgodfahim.github.io/fto/combined.xml",
    "https://evilgodfahim.github.io/nytop/combined.xml",
    "https://theconversation.com/global/home-page.atom",
    "https://politepaul.com/fd/R39To2fYhqqO.xml",
    "https://evilgodfahim.github.io/lemonde/combined.xml",
    "https://eurasiantimes.com/feed/",
    "http://www.irinnews.org/rss/conflict.xml",
    "https://www.bloomberg.com/politics/feeds/site.xml",
    "https://saiia.org.za/thematic-area/foreign-policy/feed/",
    "https://www.vtforeignpolicy.com/feed/",
    "https://medium.com/feed/tag/foreign-policy",
    "https://www.hrw.org/taxonomy/term/9653/feed",
    "https://theconversation.com/us/topics/geopolitics-4230/articles.atom",
    "https://geopoliticaleconomy.substack.com/feed",
    "https://www.newgeopolitics.org/feed/",
    "https://ipdefenseforum.com/feed/",
    "http://www.nytimes.com/topic/subject/international-relations/rss.xml",
    "http://www.irinnews.org/irin.xml",
    "https://feeds.feedburner.com/LongWarJournalSiteWide",
    "https://gulfif.org/feed/",
    "https://ecfr.eu/feed/",
    "https://www.spiegel.de/international/index.rss",
    "https://mondediplo.com/backend",
    "https://eng.globalaffairs.ru/rss",
    "https://ddgeopolitics.substack.com/feed",
    "https://knowledge.skema.edu/tag/geopolitics/feed/",
    "https://lansinginstitute.org/category/geopolitics/feed/",
    "https://geopolitics.co/feed/",
    "https://feeds.feedburner.com/worldpoliticsreview",
    "https://www.rand.org/blog.xml",
    "https://thegeopolitics.com/feed/",
    "https://fpif.org/feed/",
    "https://www.fpri.org/feed/",
    "https://www.chathamhouse.org/path/whatsnew.xml",
    "https://www.politico.eu/section/foreign-affairs/feed/",
    "https://www.moonofalabama.org/atom.xml",
    "https://southfront.press/feed/",
    "https://geopoliticaleconomy.com/feed/",
    "https://geopoliticsreport.substack.com/feed",
    "https://www.modadgeopolitics.com/feed",
    "https://geopoliticsagi.substack.com/feed",
    "https://katehon.com/en/rss.xml",
    "https://www.theguardian.com/us/commentisfree/rss",
    "https://evilgodfahim.github.io/intop/filtered.xml",
    "https://blogs.timesofindia.indiatimes.com/feed/defaultrss",
    "https://indianexpress.com/section/explained/feed/",
    "https://indianexpress.com/section/opinion/editorials/feed/",
    "https://indianexpress.com/section/opinion/feed/",
    "https://www.thehindu.com/opinion/?service=rss",
    "https://www.thehindu.com/opinion/editorial/?service=rss",
    "https://www.hindustantimes.com/feeds/rss/opinion/rssfeed.xml",
    "https://feeds.feedburner.com/Consortiumnewscom",
    "https://evilgodfahim.github.io/org/daily_feed.xml",
    "https://www.middleeasteye.net/rss",
    "https://evilgodfahim.github.io/fpost/output/merged.xml",
    "https://evilgodfahim.github.io/nytint/combined.xml",
    "https://politepaul.com/fd/xZ040wnIFK1J.xml",
    "https://www.middleeastmonitor.com/feed/",
    "https://www.themoscowtimes.com/rss/news",
    "https://www.aljazeera.com/Services/Rss/?PostingId=2007731105943979989",
    "https://www.scmp.com/rss/5/feed",
    "https://www.thehindu.com/news/international/?service=rss",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://politepaul.com/fd/BzFhFtawKQrt.xml",
    "https://www.scmp.com/rss/318199/feed",
    "https://politepaul.com/fd/x7ZadWalRg3O.xml",
    # ... rest kept unchanged ...
]

# ---- UTILITIES (kept mostly as original) ----
def normalize_datetime(dt):
    if dt is None:
        return datetime.now(timezone.utc)
    if isinstance(dt, datetime):
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    return datetime.now(timezone.utc)

def contains_bangladesh(text):
    if text is None:
        return False
    return 'bangladesh' in text.lower()

def get_entry_id(entry):
    link = entry.get('link', '')
    title = entry.get('title', '')
    unique_str = f"{link}{title}"
    return hashlib.md5(unique_str.encode()).hexdigest()

def escape_xml(text):
    if not text:
        return ""
    text = str(text)
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    text = text.replace('"', "&quot;")
    text = text.replace("'", "&apos;")
    return text

def extract_image(entry):
    # entry is a dict-like object from feedparser
    # media_content
    media_content = entry.get('media_content') or []
    for media in media_content:
        url = media.get('url') or media.get('href')
        if url:
            return url
    # media_thumbnail
    media_thumbnail = entry.get('media_thumbnail') or []
    for thumb in media_thumbnail:
        url = thumb.get('url') or thumb.get('href')
        if url:
            return url
    # enclosures
    for enc in entry.get('enclosures', []):
        if enc.get('type', '').startswith('image/'):
            return enc.get('href') or enc.get('url')
    # image dict
    img = entry.get('image')
    if isinstance(img, dict):
        return img.get('href') or img.get('url')
    # links with image type
    for l in entry.get('links', []):
        if l.get('type', '').startswith('image/'):
            return l.get('href') or l.get('url')
        if l.get('rel') == 'enclosure' and l.get('type', '').startswith('image/'):
            return l.get('href') or l.get('url')
    # parse html content for <img>
    content = ""
    if entry.get('content'):
        content = entry['content'][0].get('value', '')
    elif entry.get('summary'):
        content = entry.get('summary')
    elif entry.get('description'):
        content = entry.get('description')
    if content:
        m = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', content, re.IGNORECASE)
        if m:
            return m.group(1)
    return None

# ---- NETWORK / PARSING (threaded, with timeouts & retries) ----
def make_session():
    s = requests.Session()
    # Retry strategy
    retry = Retry(
        total=RETRIES,
        backoff_factor=BACKOFF_FACTOR,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "HEAD"],
        raise_on_status=False
    )
    adapter = HTTPAdapter(max_retries=retry)
    s.mount("http://", adapter)
    s.mount("https://", adapter)
    # sensible headers
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (compatible; feed-fetcher/1.0; +https://github.com)"
    })
    return s

def fetch_feed(session, feed_url):
    try:
        resp = session.get(feed_url, timeout=TIMEOUT)
        resp.raise_for_status()
        parsed = feedparser.parse(resp.content)
        return parsed
    except Exception as e:
        print(f"Error fetching {feed_url}: {e}")
        return None

def fetch_all_feeds():
    all_entries = []
    seen_ids = set()
    total_images = 0
    session = make_session()

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {ex.submit(fetch_feed, session, u): u for u in FEEDS}
        for fut in concurrent.futures.as_completed(futures):
            feed_url = futures[fut]
            print(f"Fetching: {feed_url}")
            parsed = None
            try:
                parsed = fut.result()
            except Exception as e:
                print(f"  Worker error for {feed_url}: {e}")
                parsed = None

            if not parsed:
                continue

            # safe access to entries
            entries = parsed.entries or []
            source_title = (parsed.feed.get('title') if isinstance(parsed.feed, dict) else getattr(parsed.feed, 'title', None)) or feed_url

            for entry in entries:
                title = entry.get('title', '')
                link = entry.get('link', '')
                description = entry.get('description', '') or entry.get('summary', '')

                if not (contains_bangladesh(title) or contains_bangladesh(link) or contains_bangladesh(description)):
                    continue

                entry_id = get_entry_id(entry)
                if entry_id in seen_ids:
                    continue
                seen_ids.add(entry_id)

                # publication date
                pub_date_struct = entry.get('published_parsed') or entry.get('updated_parsed')
                if pub_date_struct:
                    pub_date = datetime(*pub_date_struct[:6], tzinfo=timezone.utc)
                else:
                    pub_date = datetime.now(timezone.utc)

                # image
                image = extract_image(entry)
                if image:
                    total_images += 1
                    print(f"  📸 Image found: {image[:60]}...")

                all_entries.append({
                    'title': title,
                    'link': link,
                    'description': description,
                    'pub_date': pub_date,
                    'source': source_title,
                    'image': image
                })

    all_entries.sort(key=lambda x: x['pub_date'], reverse=True)
    print(f"\n✅ Found {len(all_entries)} Bangladesh articles")
    print(f"📸 {total_images} articles have images")
    return all_entries[:500]

# ---- existing feed loader / merge / output (kept behavior) ----
def load_existing_feed():
    if not os.path.exists('feed.xml'):
        return []
    try:
        import xml.etree.ElementTree as ET
        tree = ET.parse('feed.xml')
        root = tree.getroot()
        entries = []
        for item in root.findall('.//item'):
            title = item.find('title').text if item.find('title') is not None else ''
            link = item.find('link').text if item.find('link') is not None else ''
            description = item.find('description').text if item.find('description') is not None else ''
            pub_date_str = item.find('pubDate').text if item.find('pubDate') is not None else ''
            image = None
            img_elem = item.find("{http://search.yahoo.com/mrss/}thumbnail")
            if img_elem is not None:
                image = img_elem.get("url")
            else:
                enc_elem = item.find("enclosure")
                if enc_elem is not None and enc_elem.get("type", "").startswith("image/"):
                    image = enc_elem.get("url")
            try:
                pub_date = datetime.strptime(pub_date_str, '%a, %d %b %Y %H:%M:%S %z')
            except:
                try:
                    pub_date = datetime.strptime(pub_date_str, '%a, %d %b %Y %H:%M:%S')
                    pub_date = pub_date.replace(tzinfo=timezone.utc)
                except:
                    pub_date = datetime.now(timezone.utc)
            entries.append({
                'title': title,
                'link': link,
                'description': description,
                'pub_date': pub_date,
                'source': '',
                'image': image
            })
        return entries
    except Exception as e:
        print(f"Error loading existing feed.xml: {e}")
        return []

def merge_entries(existing, new):
    seen_ids = set()
    merged = []
    for entry in new:
        entry_id = hashlib.md5(f"{entry['link']}{entry['title']}".encode()).hexdigest()
        if entry_id not in seen_ids:
            seen_ids.add(entry_id)
            entry['pub_date'] = normalize_datetime(entry['pub_date'])
            merged.append(entry)
    for entry in existing:
        entry_id = hashlib.md5(f"{entry['link']}{entry['title']}".encode()).hexdigest()
        if entry_id not in seen_ids:
            seen_ids.add(entry_id)
            entry['pub_date'] = normalize_datetime(entry['pub_date'])
            merged.append(entry)
    merged.sort(key=lambda x: x['pub_date'], reverse=True)
    return merged[:500]

def create_rss_feed(entries):
    xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml_lines.append('<rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/">')
    xml_lines.append('  <channel>')
    xml_lines.append('    <title>Bangladesh News Aggregator</title>')
    xml_lines.append('    <link>https://github.com</link>')
    xml_lines.append('    <description>Aggregated news articles about Bangladesh from multiple sources</description>')
    xml_lines.append('    <language>en</language>')
    xml_lines.append(f'    <lastBuildDate>{datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")}</lastBuildDate>')
    for entry in entries:
        xml_lines.append('    <item>')
        xml_lines.append(f'      <title>{escape_xml(entry["title"])}</title>')
        xml_lines.append(f'      <link>{escape_xml(entry["link"])}</link>')
        xml_lines.append(f'      <description>{escape_xml(entry["description"])}</description>')
        xml_lines.append(f'      <pubDate>{entry["pub_date"].strftime("%a, %d %b %Y %H:%M:%S +0000")}</pubDate>')
        xml_lines.append(f'      <guid isPermaLink="true">{escape_xml(entry["link"])}</guid>')
        if entry.get('image'):
            xml_lines.append(f'      <media:thumbnail url="{escape_xml(entry["image"])}" />')
            xml_lines.append(f'      <media:content url="{escape_xml(entry["image"])}" medium="image" />')
            xml_lines.append(f'      <enclosure url="{escape_xml(entry["image"])}" type="image/jpeg" />')
        xml_lines.append('    </item>')
    xml_lines.append('  </channel>')
    xml_lines.append('</rss>')
    with open('feed.xml', 'w', encoding='utf-8') as f:
        f.write('\n'.join(xml_lines))

# ---- main ----
if __name__ == '__main__':
    print("=" * 70)
    print("Bangladesh News Aggregation (fixed)")
    print("=" * 70)
    existing_entries = load_existing_feed()
    print(f"Loaded {len(existing_entries)} existing entries")
    new_entries = fetch_all_feeds()
    all_entries = merge_entries(existing_entries, new_entries)
    print(f"\nTotal entries after merge: {len(all_entries)}")
    print(f"📸 Entries with images: {sum(1 for e in all_entries if e.get('image'))}")
    create_rss_feed(all_entries)
    print("\n✅ RSS feed created successfully (feed.xml)")
    print("=" * 70)