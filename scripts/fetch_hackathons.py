#!/usr/bin/env python3
"""
Hackathon Data Aggregator & Orchestrator
- Aggregates curated data with external sources: Devpost, HackerEarth, Dare2Compete (Unstop), MLH, Eventbrite
- Normalizes and deduplicates results without changing the main data schema
- Enriches Indian hackathons with region='India' when applicable
- Saves full dataset to data/hackathons.json and India-focused subset to data/india_hackathons.json

Note: This script uses public HTML pages and available APIs where possible.
If any source blocks bots or rate-limits, the scraper handles gracefully with fallbacks.
"""

import json
import os
import re
import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

import requests
from bs4 import BeautifulSoup

# -----------------------------
# Utilities
# -----------------------------
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    )
}

ISO_Z_SUFFIX = "%Y-%m-%dT%H:%M:%SZ"

INDIA_KEYWORDS = [
    "india", "indian", "bangalore", "bengaluru", "delhi", "mumbai", "pune", "hyderabad",
    "chennai", "kolkata", "ahmedabad", "kochi", "jaipur", "noida", "gurgaon", "gurugram",
]


def parse_date(text: str) -> Optional[str]:
    """Parse a date string into ISO8601 Z format when possible."""
    if not text:
        return None
    text = text.strip()
    # If already ISO 8601 Z
    if re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$", text):
        return text
    # Try common human formats
    for fmt in [
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%d %b %Y",
        "%b %d, %Y",
        "%B %d, %Y",
    ]:
        try:
            dt = datetime.strptime(text, fmt).replace(tzinfo=timezone.utc)
            return dt.strftime(ISO_Z_SUFFIX)
        except Exception:
            continue
    return None


def normalize_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure the item follows the main data schema keys without altering schema.
    Expected keys (kept as-is):
    - name, description, start_date, end_date, registration_deadline,
      location, type, prizePool, registration_link, website_link,
      organizer, tags, source
    """
    defaults = {
        "name": None,
        "description": None,
        "start_date": None,
        "end_date": None,
        "registration_deadline": None,
        "location": None,
        "type": None,
        "prizePool": None,
        "registration_link": None,
        "website_link": None,
        "organizer": None,
        "tags": [],
        "source": None,
    }
    out = {**defaults, **item}

    for k in ["start_date", "end_date", "registration_deadline"]:
        if out.get(k):
            parsed = parse_date(str(out[k]))
            out[k] = parsed or out[k]

    if isinstance(out.get("tags"), str):
        out["tags"] = [out["tags"]]
    if out.get("tags") is None:
        out["tags"] = []

    for k, v in list(out.items()):
        if isinstance(v, str):
            out[k] = v.strip()

    return out


def is_india_event(item: Dict[str, Any]) -> bool:
    loc = (item.get("location") or "").lower()
    text = f"{item.get('name','')}\n{item.get('description','')}".lower()
    tags = [t.lower() for t in (item.get("tags") or [])]

    if any(k in loc for k in INDIA_KEYWORDS):
        return True
    if any(k in text for k in INDIA_KEYWORDS):
        return True
    if "india" in tags:
        return True
    if any(s in loc for s in ["global", "worldwide", "virtual", "online"]):
        return True
    return False


def add_india_region_flag(items: List[Dict[str, Any]]) -> None:
    for it in items:
        try:
            if is_india_event(it) and not it.get("region"):
                it["region"] = "India"
        except Exception:
            continue


# -----------------------------
# Source fetchers
# -----------------------------

def fetch_devpost() -> List[Dict[str, Any]]:
    url = "https://devpost.com/hackathons"
    items: List[Dict[str, Any]] = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        cards = soup.select(".hackathon-tile, .hackathon-tile-wrapper, .challenge-list .challenge")
        for c in cards[:60]:
            name_el = c.select_one("h3, h2")
            name = name_el.get_text(strip=True) if name_el else None
            link_el = c.select_one("a[href*='/hackathons/'], a[href*='/challenges/']")
            link = None
            if link_el and link_el.get("href"):
                href = link_el.get("href")
                link = "https://devpost.com" + href if href.startswith("/") else href
            desc_el = c.select_one(".challenge-description, .hackathon-desc, .content p, p")
            desc = desc_el.get_text(strip=True) if desc_el else None
            item = normalize_item({
                "name": name,
                "description": desc,
                "registration_link": link,
                "website_link": link,
                "location": "Global/Virtual",
                "type": "online",
                "organizer": "Devpost",
                "tags": ["devpost"],
                "source": "Devpost",
            })
            if item.get("name"):
                items.append(item)
    except Exception:
        return items
    return items


def fetch_hackerearth() -> List[Dict[str, Any]]:
    url = "https://www.hackerearth.com/challenges/hackathon/"
    items: List[Dict[str, Any]] = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        for card in soup.select(".challenge-card-modern, .upcoming.challenge-list, .ongoing.challenge-list")[:60]:
            name_el = card.select_one(".challenge-list-title, .event-title, h3, h2")
            name = name_el.get_text(strip=True) if name_el else None
            link_el = card.select_one("a[href]")
            link = link_el.get("href") if link_el else None
            if link and link.startswith("/"):
                link = "https://www.hackerearth.com" + link
            meta = card.get_text(" ", strip=True)
            item = normalize_item({
                "name": name,
                "description": meta,
                "registration_link": link,
                "website_link": link,
                "location": "Global/Virtual",
                "type": "online",
                "organizer": "HackerEarth",
                "tags": ["hackerearth"],
                "source": "HackerEarth",
            })
            if item.get("name"):
                items.append(item)
    except Exception:
        return items
    return items


def fetch_unstop() -> List[Dict[str, Any]]:
    url = "https://unstop.com/hackathons"
    items: List[Dict[str, Any]] = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        for card in soup.select("a.event-card, .event-card a[href]")[:60]:
            name = card.get("title") or card.get_text(" ", strip=True)
            link = card.get("href")
            if link and link.startswith("/"):
                link = "https://unstop.com" + link
            loc_el = card.select_one(".event-location, .loc, .sub-info")
            loc = loc_el.get_text(strip=True) if loc_el else "India"
            item = normalize_item({
                "name": name,
                "description": "Unstop hackathon",
                "registration_link": link,
                "website_link": link,
                "location": loc or "India",
                "type": "online",
                "organizer": "Unstop",
                "tags": ["unstop", "dare2compete"],
                "source": "Dare2Compete/Unstop",
            })
            if item.get("name"):
                items.append(item)
    except Exception:
        return items
    return items


def fetch_mlh() -> List[Dict[str, Any]]:
    url = "https://mlh.io/seasons/2025/events"
    items: List[Dict[str, Any]] = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        for card in soup.select(".event-wrapper, .event-card")[:80]:
            name_el = card.select_one(".event-name, h3, h2")
            name = name_el.get_text(strip=True) if name_el else None
            link_el = card.select_one("a[href]")
            link = link_el.get("href") if link_el else None
            if link and link.startswith("/"):
                link = "https://mlh.io" + link
            loc_el = card.select_one(".event-location, .location")
            loc = loc_el.get_text(strip=True) if loc_el else "Global/Virtual"
            date_el = card.select_one(".event-date, .date")
            date_text = date_el.get_text(strip=True) if date_el else None
            item = normalize_item({
                "name": name,
                "description": date_text,
                "registration_link": link,
                "website_link": link,
                "location": loc,
                "type": "in-person" if loc and loc.lower() != "online" else "online",
                "organizer": "MLH",
                "tags": ["mlh"],
                "source": "MLH",
            })
            if item.get("name"):
                items.append(item)
    except Exception:
        return items
    return items


def fetch_eventbrite() -> List[Dict[str, Any]]:
    url = "https://www.eventbrite.com/d/online/hackathon/"
    items: List[Dict[str, Any]] = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        for card in soup.select(".search-event-card-wrapper, .discover-search-desktop-card")[:60]:
            name_el = card.select_one(".eds-event-card__formatted-name--is-clamped, h3, h2")
            name = name_el.get_text(strip=True) if name_el else None
            link_el = card.select_one("a[href]")
            link = link_el.get("href") if link_el else None
            if link and link.startswith("/"):
                link = "https://www.eventbrite.com" + link
            org_el = card.select_one(".card-text--truncated__one, .eds-text-bs--fixed")
            org = org_el.get_text(strip=True) if org_el else "Eventbrite"
            item = normalize_item({
                "name": name,
                "description": "Eventbrite hackathon",
                "registration_link": link,
                "website_link": link,
                "location": "Global/Virtual",
                "type": "online",
                "organizer": org,
                "tags": ["eventbrite"],
                "source": "Eventbrite",
            })
            if item.get("name"):
                items.append(item)
    except Exception:
        return items
    return items


def canonical_id(item: Dict[str, Any]) -> str:
    link = (item.get("registration_link") or item.get("website_link") or "").lower().strip()
    if link:
        m = re.sub(r"^https?://(www\.)?", "", link)
        m = m.split("?")[0].rstrip("/")
        return m
    base = (item.get("name") or "").lower().strip()
    base = re.sub(r"\s+", "-", base)
    return base


def merge_sources(sources: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    seen: Dict[str, Dict[str, Any]] = {}
    for lst in sources:
        for it in lst:
            if not it.get("name"):
                continue
            cid = canonical_id(it)
            if cid in seen:
                existing = seen[cid]
                for k, v in it.items():
                    if v in (None, "", [], {}):
                        continue
                    if existing.get(k) in (None, "", [], {}):
                        existing[k] = v
                    if k == "description" and isinstance(v, str) and isinstance(existing.get(k), str):
                        if len(v) > len(existing[k]):
                            existing[k] = v
                    if k == "prizePool" and isinstance(v, str):
                        if not existing.get(k) or ("$" in v or "₹" in v or "USD" in v.upper() or "INR" in v.upper()):
                            existing[k] = v
            else:
                seen[cid] = dict(it)
    return list(seen.values())


def main() -> None:
    print("🚀 Aggregating hackathons from curated and external sources...")
    os.makedirs("data", exist_ok=True)

    curated = get_curated_hackathons()

    external_batches: List[List[Dict[str, Any]]] = []
    for fetcher in (fetch_devpost, fetch_hackerearth, fetch_unstop, fetch_mlh, fetch_eventbrite):
        try:
            print(f"Fetching from {fetcher.__name__}...")
            data = fetcher()
            print(f"  -> {len(data)} items")
            external_batches.append(data)
            time.sleep(0.8)
        except Exception as e:
            print(f"  !! Failed {fetcher.__name__}: {e}")
            external_batches.append([])

    merged = merge_sources([curated] + external_batches)

    add_india_region_flag(merged)

    now_iso = datetime.now(timezone.utc).strftime(ISO_Z_SUFFIX)

    # Keep existing schema philosophy: produce a flat array plus light metadata
    output = {
        "update_info": {
            "current_date": now_iso,
            "sources": ["curated", "devpost", "hackerearth", "unstop", "mlh", "eventbrite"],
        },
        "all": merged,
    }

    # Save full dataset
    with open("data/hackathons.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    # India subset: items with region set to India or open-to-India
    india_items = [x for x in merged if is_india_event(x)]
    india_output = {
        "update_info": output["update_info"],
        "all": india_items,
    }
    with open("data/india_hackathons.json", "w", encoding="utf-8") as f:
        json.dump
