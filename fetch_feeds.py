import feedparser
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
import hashlib
import os
import re

# List of feed URLs
FEEDS = [
    "https://asiatimes.com/feed/",
    "https://politepol.com/fd/TefnRxuxFzO0.xml",
    "https://evilgodfahim.github.io/csis/rss.xml",
    "https://politepol.com/fd/9RMAFvRRGLst.xml",
    "https://www.globalpolicyjournal.com/blog/author/%2A/feed",
    "https://www.e-ir.info/feed/",
    "https://www.theglobalist.com/feed/",
    "https://responsiblestatecraft.org/feed/",
    "https://politepol.com/fd/ffERiOdKxWlq.xml",
    "https://politepol.com/fd/dCWMZKe7BJqi.xml",
    "https://politepol.com/fd/YJRa9YOT7CyB.xml",
    "https://meduza.io/rss/en/all",
    "https://politepol.com/fd/JsMAwSx6Pkbr.xml",
    "https://evilgodfahim.github.io/alm/combined.xml",
    "https://evilgodfahim.github.io/start/combined.xml",
    "https://politepol.com/fd/GbcosKoaAE22.xml",
    "https://www.noemamag.com/article-topic/geopolitics-globalization/feed/",
    "https://zeihan.com/feed/",
    "https://politepol.com/fd/ELc5hcluIkDO.xml",
    "https://original.antiwar.com/feed/",
    "https://www.atlanticcouncil.org/feed/",
    "https://warontherocks.com/feed/",
    "https://www.thehindu.com/opinion/editorial/?service=rss",
    "https://politepol.com/fd/aCEp2lWYu3Jn.xml",
    "https://evilgodfahim.github.io/fto/combined.xml",
    "https://evilgodfahim.github.io/nytop/combined.xml",
    "https://theconversation.com/global/home-page.atom",
    "https://politepol.com/fd/R39To2fYhqqO.xml",
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
    "https://politepol.com/fd/xZ040wnIFK1J.xml",
    "https://www.middleeastmonitor.com/feed/",
    "https://www.themoscowtimes.com/rss/news",
    "https://www.aljazeera.com/Services/Rss/?PostingId=2007731105943979989",
    "https://www.scmp.com/rss/5/feed",
    "https://www.thehindu.com/news/international/?service=rss",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://politepol.com/fd/BzFhFtawKQrt.xml",
    "https://www.scmp.com/rss/318199/feed",
    "https://politepol.com/fd/x7ZadWalRg3O.xml",
    "https://www.ft.com/rss/world",
    "https://feeds.guardian.co.uk/theguardian/world/rss",
    "https://evilgodfahim.github.io/ap-merge/output/merged.xml",
    "https://news.un.org/feed/subscribe/en/news/all/rss.xml",
    "https://evilgodfahim.github.io/bdnint/output/merged.xml",
    "https://evilgodfahim.github.io/feint/output/merged.xml",
    "https://evilgodfahim.github.io/NAINT/output/merged.xml",
    "https://politepol.com/fd/ejjxAclQ0Ij0.xml",
    "https://politepol.com/fd/RVHJinKtHIEp.xml",
    "https://politepol.com/fd/MQdEEfACJVgu.xml",
    "https://www.jpost.com/Rss/RssFeedsMiddleEastNews.aspx",
    "https://politepol.com/fd/SvkVrxDkZguQ.xml",
    "https://news.google.com/rss/search?q=source:Reuters&hl=en-US&gl=US&ceid=US:en",
    "https://balkaninsight.com/feed/",
    "https://www.nytimes.com/services/xml/rss/nyt/Europe.xml",
    "https://www.europeanvoice.com/feed/",
    "https://www.france24.com/en/europe/rss",
    "https://feeds.feedburner.com/euronews/en/home/",
    "https://www.theguardian.com/world/middleeast/rss",
    "https://www.nytimes.com/services/xml/rss/nyt/MiddleEast.xml",
    "https://www.al-monitor.com/pulse/home/rssfeeds/frontpage-rss/maincontent/Front_Page.default.rss",
    "https://www.newindianexpress.com/World/rssfeed/?id=171&getXmlFeed=true",
    "https://economictimes.indiatimes.com/rssfeeds/858478126.cms",
    "https://www.hindustantimes.com/feeds/rss/world-news/rssfeed.xml",
    "https://timesofindia.indiatimes.com/rssfeeds/296589292.cms",
    "https://www.cgtn.com/subscribe/rss/section/world.xml",
    "http://www.channelnewsasia.com/rss/latest_cna_world_rss.xml",
    "https://chinadigitaltimes.net/feed/",
    "https://feeds.feedburner.com/themoscowtimes/opinion",
    "https://english.pravda.ru/export.xml",
    "https://tass.com/rss/v2.xml",
    "https://rt.com/rss/",
    "https://en.rian.ru/export/rss2/index.xml",
    "https://themoscowtimes.com/feeds/main.xml",
    "https://www.dailywire.com/feeds/rss.xml",
    "https://chaski.huffpost.com/us/auto/vertical/world-news",
    "https://feeds.guardian.co.uk/theguardian/world/china/rss",
    "https://www.democracynow.org/democracynow.rss",
    "https://spectatorworld.com/feed/",
    "https://thehill.com/taxonomy/term/43/feed",
    "https://time.com/feed/",
    "https://feeds.feedburner.com/AtlanticInternational",
    "https://www.straitstimes.com/news/asia/rss.xml",
    "http://southasiamonitor.org/rss.xml",
    "http://www.hrw.org/rss/taxonomy/10",
    "https://timesca.com/feed/",
    "http://www.channelnewsasia.com/rss/latest_cna_asiapac_rss.xml",
    "https://www.theguardian.com/world/asia/rss",
    "https://www.nytimes.com/services/xml/rss/nyt/AsiaPacific.xml",
    "https://www.japantimes.co.jp/news_category/asia-pacific/feed/",
    "https://feedx.net/rss/ap.xml",
    "http://rss.dw.de/rdf/rss-en-world",
    "https://feed.theepochtimes.com/world/feed",
    "https://www.straitstimes.com/news/world/rss.xml",
    "https://feeds.abcnews.com/abcnews/internationalheadlines",
    "https://rsshub.app/reuters/world",
    "https://evilgodfahim.github.io/wl/article.xml",
    "http://rss.cnn.com/rss/edition.rss",
    "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
    "https://www.thehindu.com/feeder/default.rss",
    "https://feeds.feedburner.com/ndtvnews-top-stories",
    "https://www.livemint.com/rss/money",
    "https://www.dawn.com/feeds/home/",
    "https://www.geo.tv/rss/1/0",
    "https://tribune.com.pk/feed/",
    "https://nation.com.pk/rss/",
    "https://dailytimes.com.pk/feed/",
    "http://www.xinhuanet.com/english/rss/topnews.xml",
    "https://www.globaltimes.cn/rss/index.xml",
    "https://rss.cgtn.com/rss/english/world.xml",
    "https://www.scmp.com/rss/91/feed",
    "https://www.kyivpost.com/rss",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://feeds.washingtonpost.com/rss/world",
    "https://feeds.npr.org/1001/rss.xml",
    "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "http://feeds.foxnews.com/foxnews/latest",
    "https://feeds.a.dj.com/rss/RSSWorldNews.xml",
    "https://www.telegraph.co.uk/news/rss.xml",
    "https://www.independent.co.uk/news/world/rss",
    "https://www.france24.com/en/rss",
    "https://rss.dw.com/rdf/rss-en-all",
    "https://www.euronews.com/rss?format=xml",
    "https://www.ansamed.info/ansamed/en/ansamed_rss.xml",
    "https://www3.nhk.or.jp/rss/news/cat0.xml",
    "https://www.japantimes.co.jp/feed",
    "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml",
    "http://www.koreaherald.com/common/rss_xml.php?ct=101",
    "https://www.abc.net.au/news/feed/51120/rss.xml",
    "https://www.smh.com.au/rss/feed.xml",
    "https://www.bangkokpost.com/rss/data/topstories.xml",
    "https://www.middleeasteye.net/rss",
    "https://www.arabnews.com/rss.xml",
    "https://www.jpost.com/rss/rssfeedsheadlines.aspx",
    "https://allafrica.com/tools/headlines/rdf/latest/headlines.rdf",
    "http://feeds.news24.com/articles/news24/TopStories/rss",
    "https://www.cbc.ca/cmlink/rss-topstories",
    "https://globalnews.ca/feed/",
    "https://en.mercopress.com/rss/",
    "https://mexiconewsdaily.com/feed/"
]

def normalize_datetime(dt):
    """Normalize datetime to UTC timezone-aware datetime"""
    if dt is None:
        return datetime.now(timezone.utc)

    # If it's already a datetime object
    if isinstance(dt, datetime):
        # If naive, assume UTC
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        # If aware, convert to UTC
        return dt.astimezone(timezone.utc)

    # If it's something else, return current time
    return datetime.now(timezone.utc)

def contains_bangladesh(text):
    """Check if text contains 'bangladesh' (case-insensitive)"""
    if text is None:
        return False
    return 'bangladesh' in text.lower()

def get_entry_id(entry):
    """Generate unique ID for an entry"""
    link = entry.get('link', '')
    title = entry.get('title', '')
    unique_str = f"{link}{title}"
    return hashlib.md5(unique_str.encode()).hexdigest()

def extract_image(entry):
    """Extract thumbnail/preview image from feed entry"""
    # Try media:content
    if hasattr(entry, "media_content") and entry.media_content:
        for media in entry.media_content:
            if "url" in media:
                return media["url"]
    
    # Try media:thumbnail
    if hasattr(entry, "media_thumbnail") and entry.media_thumbnail:
        for thumb in entry.media_thumbnail:
            if "url" in thumb:
                return thumb["url"]
    
    # Try enclosures
    if hasattr(entry, "enclosures") and entry.enclosures:
        for enc in entry.enclosures:
            if enc.get("type", "").startswith("image/"):
                return enc.get("url", "")
    
    # Try image dict
    if hasattr(entry, "image") and isinstance(entry.image, dict):
        return entry.image.get("href") or entry.image.get("url")
    
    # Try links with image type
    if hasattr(entry, "links"):
        for l in entry.links:
            if l.get("type", "").startswith("image/"):
                return l.get("href") or l.get("url")
            # Check for rel="enclosure" with image
            if l.get("rel") == "enclosure" and l.get("type", "").startswith("image/"):
                return l.get("href") or l.get("url")
    
    # Try parsing HTML content for images
    content = ""
    if hasattr(entry, "content") and entry.content:
        content = entry.content[0].get("value", "")
    elif hasattr(entry, "summary"):
        content = entry.summary
    elif hasattr(entry, "description"):
        content = entry.description
    
    if content:
        # Look for img tags
        img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', content, re.IGNORECASE)
        if img_match:
            return img_match.group(1)
    
    return None

def fetch_all_feeds():
    """Fetch and filter all feeds for Bangladesh-related content"""
    all_entries = []
    seen_ids = set()
    total_images = 0

    for feed_url in FEEDS:
        try:
            print(f"Fetching: {feed_url}")
            feed = feedparser.parse(feed_url)

            for entry in feed.entries:
                # Check if Bangladesh is mentioned in title, link, or description
                title = entry.get('title', '')
                link = entry.get('link', '')
                description = entry.get('description', '') or entry.get('summary', '')

                if (contains_bangladesh(title) or 
                    contains_bangladesh(link) or 
                    contains_bangladesh(description)):

                    entry_id = get_entry_id(entry)

                    # Skip duplicates
                    if entry_id in seen_ids:
                        continue

                    seen_ids.add(entry_id)

                    # Extract publication date
                    pub_date = entry.get('published_parsed') or entry.get('updated_parsed')
                    if pub_date:
                        pub_date = datetime(*pub_date[:6], tzinfo=timezone.utc)
                    else:
                        pub_date = datetime.now(timezone.utc)

                    # Extract image
                    image = extract_image(entry)
                    if image:
                        total_images += 1
                        print(f"  📸 Image found: {image[:60]}...")

                    all_entries.append({
                        'title': title,
                        'link': link,
                        'description': description,
                        'pub_date': pub_date,
                        'source': feed.feed.get('title', feed_url),
                        'image': image
                    })
        except Exception as e:
            print(f"Error fetching {feed_url}: {e}")

    # Sort by date (newest first)
    all_entries.sort(key=lambda x: x['pub_date'], reverse=True)

    # Keep only the latest 500 items
    print(f"\n✅ Found {len(all_entries)} Bangladesh articles")
    print(f"📸 {total_images} articles have images")
    
    return all_entries[:500]

def load_existing_feed():
    """Load existing entries from feed.xml if it exists"""
    if not os.path.exists('feed.xml'):
        return []

    try:
        tree = ET.parse('feed.xml')
        root = tree.getroot()

        entries = []
        for item in root.findall('.//item'):
            title = item.find('title').text if item.find('title') is not None else ''
            link = item.find('link').text if item.find('link') is not None else ''
            description = item.find('description').text if item.find('description') is not None else ''
            pub_date_str = item.find('pubDate').text if item.find('pubDate') is not None else ''

            # Extract image
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
                    # Try without timezone
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
    except:
        return []

def merge_entries(existing, new):
    """Merge existing and new entries, removing duplicates"""
    seen_ids = set()
    merged = []

    # Add new entries first
    for entry in new:
        entry_id = hashlib.md5(f"{entry['link']}{entry['title']}".encode()).hexdigest()
        if entry_id not in seen_ids:
            seen_ids.add(entry_id)
            # Normalize datetime
            entry['pub_date'] = normalize_datetime(entry['pub_date'])
            merged.append(entry)

    # Add existing entries that aren't duplicates
    for entry in existing:
        entry_id = hashlib.md5(f"{entry['link']}{entry['title']}".encode()).hexdigest()
        if entry_id not in seen_ids:
            seen_ids.add(entry_id)
            # Normalize datetime
            entry['pub_date'] = normalize_datetime(entry['pub_date'])
            merged.append(entry)

    # Sort by date and limit to 500
    merged.sort(key=lambda x: x['pub_date'], reverse=True)
    return merged[:500]

def create_rss_feed(entries):
    """Create RSS 2.0 feed XML with image support"""
    # Register media namespace
    ET.register_namespace('media', 'http://search.yahoo.com/mrss/')
    
    rss = ET.Element('rss', {
        'version': '2.0',
        'xmlns:media': 'http://search.yahoo.com/mrss/'
    })
    channel = ET.SubElement(rss, 'channel')

    ET.SubElement(channel, 'title').text = 'Bangladesh News Aggregator'
    ET.SubElement(channel, 'link').text = 'https://github.com'
    ET.SubElement(channel, 'description').text = 'Aggregated news articles about Bangladesh from multiple sources'
    ET.SubElement(channel, 'language').text = 'en'
    ET.SubElement(channel, 'lastBuildDate').text = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S +0000')

    for entry in entries:
        item = ET.SubElement(channel, 'item')
        ET.SubElement(item, 'title').text = entry['title']
        ET.SubElement(item, 'link').text = entry['link']
        ET.SubElement(item, 'description').text = entry['description']
        ET.SubElement(item, 'pubDate').text = entry['pub_date'].strftime('%a, %d %b %Y %H:%M:%S +0000')
        ET.SubElement(item, 'guid', isPermaLink='true').text = entry['link']
        
        # Add image if available
        if entry.get('image'):
            # Use media:thumbnail for best RSS reader support
            ET.SubElement(
                item,
                '{http://search.yahoo.com/mrss/}thumbnail',
                url=entry['image']
            )
            
            # Also add media:content for compatibility
            ET.SubElement(
                item,
                '{http://search.yahoo.com/mrss/}content',
                url=entry['image'],
                medium='image'
            )
            
            # Add enclosure for additional compatibility
            ET.SubElement(
                item,
                'enclosure',
                url=entry['image'],
                type='image/jpeg'
            )

    tree = ET.ElementTree(rss)
    ET.indent(tree, space='  ')
    tree.write('feed.xml', encoding='utf-8', xml_declaration=True)

if __name__ == '__main__':
    print("=" * 70)
    print("Bangladesh News Aggregation with Image Support")
    print("=" * 70)

    # Load existing entries
    existing_entries = load_existing_feed()
    print(f"Loaded {len(existing_entries)} existing entries")

    # Fetch new entries
    new_entries = fetch_all_feeds()

    # Merge and deduplicate
    all_entries = merge_entries(existing_entries, new_entries)
    print(f"\nTotal entries after merge: {len(all_entries)}")
    print(f"📸 Entries with images: {sum(1 for e in all_entries if e.get('image'))}")

    # Create RSS feed
    create_rss_feed(all_entries)
    print("\n✅ RSS feed created successfully (feed.xml)")
    print("=" * 70)