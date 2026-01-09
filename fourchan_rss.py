import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import email.utils

BOARDS = ["k", "ic"]

def build_feed(board):
    url = f"https://a.4cdn.org/{board}/catalog.json"
    data = requests.get(url, timeout=15).json()

    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")

    ET.SubElement(channel, "title").text = f"/{board}/ – 4chan"
    ET.SubElement(channel, "link").text = f"https://boards.4chan.org/{board}/"
    ET.SubElement(channel, "description").text = f"New threads from /{board}/"

    for page in data:
        for t in page.get("threads", []):
            item = ET.SubElement(channel, "item")

            title = (
                t.get("sub")
                or t.get("com", "").replace("<br>", " ")[:80]
                or f"Thread {t['no']}"
            )

            link = f"https://boards.4chan.org/{board}/thread/{t['no']}"

            ET.SubElement(item, "title").text = title
            ET.SubElement(item, "link").text = link
            ET.SubElement(item, "guid").text = link

            pub = datetime.utcfromtimestamp(t["time"])
            ET.SubElement(item, "pubDate").text = email.utils.format_datetime(pub)

            # Optional OP image enclosure
            if "tim" in t and "ext" in t:
                img = f"https://i.4cdn.org/{board}/{t['tim']}{t['ext']}"
                enclosure = ET.SubElement(item, "enclosure")
                enclosure.set("url", img)
                enclosure.set("type", "image/jpeg")

    tree = ET.ElementTree(rss)
    outfile = f"{board}.rss"
    tree.write(outfile, encoding="utf-8", xml_declaration=True)
    print(f"Wrote {outfile}")

for b in BOARDS:
    build_feed(b)
