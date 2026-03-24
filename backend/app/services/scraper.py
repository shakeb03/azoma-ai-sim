import json
import re
from typing import Any
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
from app.models import ScrapedListing
from app.config import settings


async def scrape_product_page(url: str) -> ScrapedListing:
    """
    Scrape a product page using Playwright.
    Extraction priority: JSON-LD schema.org Product > DOM selectors > raw text.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=settings.playwright_headless)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )
        page = await context.new_page()
        try:
            await page.goto(url, timeout=settings.playwright_timeout_ms, wait_until="networkidle")
        except PlaywrightTimeout:
            # If networkidle times out, try domcontentloaded as fallback
            try:
                await page.goto(url, timeout=settings.playwright_timeout_ms, wait_until="domcontentloaded")
            except Exception as e:
                raise RuntimeError(f"Failed to load page {url}: {e}")

        # Try JSON-LD first
        listing = await _extract_jsonld(page, url)
        if listing:
            await browser.close()
            return listing

        # Fall back to DOM extraction
        listing = await _extract_dom(page, url)
        await browser.close()
        return listing


async def _extract_jsonld(page: Any, url: str) -> ScrapedListing | None:
    """Extract product data from schema.org JSON-LD markup."""
    scripts = await page.eval_on_selector_all(
        'script[type="application/ld+json"]',
        "els => els.map(e => e.textContent)"
    )
    for script_text in scripts:
        try:
            data = json.loads(script_text)
        except json.JSONDecodeError:
            continue

        # Handle @graph arrays
        items = data if isinstance(data, list) else [data]
        for item in items:
            if isinstance(item, dict) and item.get("@type") in ("Product", "product"):
                title = item.get("name", "")
                description = item.get("description", "")
                specs: dict[str, str] = {}

                # Extract specs from additionalProperty
                for prop in item.get("additionalProperty", []):
                    name = prop.get("name", "")
                    value = prop.get("value", "")
                    if name and value:
                        specs[name] = str(value)

                # Extract from offers
                offers = item.get("offers", {})
                if isinstance(offers, list):
                    offers = offers[0] if offers else {}
                if offers.get("price"):
                    specs["price"] = f"{offers.get('priceCurrency', '')} {offers.get('price', '')}".strip()

                if title:
                    raw_text = await page.inner_text("body")
                    return ScrapedListing(
                        url=url,
                        title=title,
                        description=description[:1000],
                        specs=specs,
                        raw_text=raw_text[:5000],
                    )
    return None


async def _extract_dom(page: Any, url: str) -> ScrapedListing:
    """Fall back to DOM selector-based extraction."""
    # Title
    title = ""
    for selector in ["h1[itemprop='name']", "h1.product-title", "h1.pdp-title", "h1"]:
        try:
            el = await page.query_selector(selector)
            if el:
                title = (await el.inner_text()).strip()
                if title:
                    break
        except Exception:
            continue
    if not title:
        title = await page.title()

    # Description
    description = ""
    for selector in [
        "meta[name='description']",
        "[itemprop='description']",
        ".product-description",
        ".pdp-description",
        "#product-description",
    ]:
        try:
            el = await page.query_selector(selector)
            if el:
                if selector.startswith("meta"):
                    description = (await el.get_attribute("content") or "").strip()
                else:
                    description = (await el.inner_text()).strip()
                if description:
                    break
        except Exception:
            continue

    # Specs from tables or dl/dt/dd
    specs: dict[str, str] = {}
    try:
        rows = await page.eval_on_selector_all(
            "table tr",
            "rows => rows.map(r => Array.from(r.querySelectorAll('th,td')).map(c => c.innerText.trim()))"
        )
        for row in rows:
            if len(row) == 2 and row[0] and row[1]:
                specs[row[0].rstrip(":")] = row[1]
    except Exception:
        pass

    if not specs:
        try:
            terms = await page.eval_on_selector_all("dl dt", "els => els.map(e => e.innerText.trim())")
            values = await page.eval_on_selector_all("dl dd", "els => els.map(e => e.innerText.trim())")
            for k, v in zip(terms, values):
                if k and v:
                    specs[k.rstrip(":")] = v
        except Exception:
            pass

    raw_text = ""
    try:
        raw_text = (await page.inner_text("body"))[:5000]
    except Exception:
        pass

    return ScrapedListing(
        url=url,
        title=title,
        description=description[:1000],
        specs=specs,
        raw_text=raw_text,
    )
