from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from datetime import datetime
import email.utils

USERNAME = "forwardobservations2.0"
OUTFILE = f"{USERNAME}_ig.rss"
URL = f"https://imginn.com/{USERNAME}/"

# --- Start Playwright ---
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(URL, timeout=30000)
    
    # Wait for posts to appear
    page.wait_for_function(
        "() => document.querySelectorAll('a[href^=\"/p/\"]').length > 0",
        timeout=15000
    )
    
    html = page.content()
    browser.close()
    
# --- Parse HTML ---
soup = BeautifulSoup(html, "html.parser")

rss = ET.Element("rss", version="2.0")
channel = ET.SubElement(rss, "channel")
ET.SubElement(channel, "title").text = f"Instagram – {USERNAME}"
ET.SubElement(channel, "link").text = URL
ET.SubElement(channel, "description").text = f"Posts by @{USERNAME} (via imginn)"

seen_posts = set()

for a in soup.find_all("a", href=True):
    href = a["href"]
    if href.startswith("/p/"):
        post_url = f"https://imginn.com{href}"
        if post_url in seen_posts:
            continue
        seen_posts.add(post_url)

        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = f"Post by {USERNAME}"
        ET.SubElement(item, "link").text = post_url
        ET.SubElement(item, "guid").text = post_url
        ET.SubElement(item, "pubDate").text = email.utils.format_datetime(datetime.utcnow())

tree = ET.ElementTree(rss)
tree.write(OUTFILE, encoding="utf-8", xml_declaration=True)
print(f"Wrote {OUTFILE} ({len(seen_posts)} posts)")
