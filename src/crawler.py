import urllib.request
from urllib.error import URLError, HTTPError
from urllib.parse import urljoin, urlparse
from html.parser import HTMLParser
import threading
import time
import src.db as db

# Configurable hardware limits simulation
MAX_QUEUE_DEPTH = 1000 # Back-pressure threshold
CRAWLER_THREADS = 3
active = False

class LinkAndTextExtractor(HTMLParser):
    def __init__(self, base_url):
        super().__init__()
        self.base_url = base_url
        self.links = []
        self.text_chunks = []
        
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for attr, value in attrs:
                if attr == 'href':
                    # Normalize URL
                    full_url = urljoin(self.base_url, value)
                    parsed = urlparse(full_url)
                    # Keep only http/https, remote fragment
                    clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                    if clean_url.startswith('http'):
                        self.links.append(clean_url)

    def handle_data(self, data):
        stripped = data.strip()
        if stripped:
            self.text_chunks.append(stripped)
            
    def get_text(self):
        return " ".join(self.text_chunks)

def crawl_worker():
    global active
    while active:
        # Check back-pressure, if queue too deep, just sleep and don't add more strain
        q_depth = db.get_queue_depth()
        if q_depth > MAX_QUEUE_DEPTH:
            time.sleep(2)
            continue
            
        row = db.get_next_pending()
        if not row:
            time.sleep(1) # Wait for jobs
            continue
            
        url_id, url, current_depth, origin_url, max_depth = row
        
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'NativePython MultiAgent Crawler'})
            with urllib.request.urlopen(req, timeout=5) as response:
                html = response.read().decode('utf-8', errors='ignore')
                
                parser = LinkAndTextExtractor(url)
                parser.feed(html)
                
                text_content = parser.get_text()
                db.mark_crawled(url_id, text_content)
                
                # If we haven't reached depth k, add discovered links
                if current_depth < max_depth:
                    for link in set(parser.links): # set ensures we don't add duplicates from same page
                        # Wait if backpressure threshold hit before we spam DB
                        while active and db.get_queue_depth() > MAX_QUEUE_DEPTH:
                            time.sleep(1)
                        # Inherit the exact origin_url (seed) for tracing
                        db.add_to_queue(link, origin_url=origin_url, depth=current_depth + 1, max_depth=max_depth)
                        
        except (URLError, HTTPError, ValueError) as e:
            # Domain non-existent, connection refused, unicode error etc.
            db.mark_failed(url_id)
        except Exception as e:
            db.mark_failed(url_id)

def start_crawling():
    global active
    active = True
    threads = []
    for _ in range(CRAWLER_THREADS):
        t = threading.Thread(target=crawl_worker)
        t.daemon = True
        t.start()
        threads.append(t)
    return threads

def stop_crawling():
    global active
    active = False

def index(origin, k):
    """Initiate a web crawl"""
    # Start the seed url at depth 0, passing along max depth k for this job
    return db.add_to_queue(origin, origin_url=origin, depth=0, max_depth=k)
