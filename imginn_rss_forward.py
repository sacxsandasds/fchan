import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from datetime import datetime
import email.utils

USERNAME = "forwardobservations2.0"   # change this
OUTFILE = f"{USERNAME}_ig.rss"

URL = f"https://imginn.com/{USERNAME}/"

html = requests.get(URL, timeout=15).text
soup = BeautifulSoup(html, "html.parser")

rss = ET.Element("rss", version="2.0")
channel = ET.SubElement(rss, "channel")

ET.SubElement(channel, "title").text = f"Instagram – {USERNAME}"
ET.SubElement(channel, "link").text = URL
ET.SubElement(channel, "description").text = f"Posts by @{USERNAME} (via imginn)"

seen = set()

for a in soup.find_all("a", href=True):
    href = a["href"]
    if href.startswith("/p/"):
        post_url = f"https://imginn.com{href}"
        if post_url in seen:
            continue
        seen.add(post_url)

        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = f"Post by {USERNAME}"
        ET.SubElement(item, "link").text = post_url
        ET.SubElement(item, "guid").text = post_url

        ET.SubElement(item, "pubDate").text = email.utils.format_datetime(
            datetime.utcnow()
        )

tree = ET.ElementTree(rss)
tree.write(OUTFILE, encoding="utf-8", xml_declaration=True)

print(f"Wrote {OUTFILE}")
