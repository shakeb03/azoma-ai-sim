import re
import httpx
from urllib.parse import urlencode, urlparse

MARKETPLACE_DOMAINS = (
    "amazon.", "walmart.", "bestbuy.", "ebay.", "target.",
    "costco.", "homedepot.", "lowes.", "wayfair.",
)


def _brand_slug(brand: str) -> str:
    """Normalize brand name to a simple slug for domain matching."""
    return re.sub(r"[^a-z0-9]", "", brand.lower())


def _is_marketplace(url: str) -> bool:
    netloc = urlparse(url).netloc.lower()
    return any(m in netloc for m in MARKETPLACE_DOMAINS)


def _extract_urls_from_ddg(html: str) -> list[str]:
    """Parse DuckDuckGo HTML results to extract result URLs."""
    # DDG HTML results contain links like /l/?uddg=<encoded-url>
    pattern = r'href="(https?://[^"]+)"'
    urls = re.findall(pattern, html)
    # Filter out DDG internal links
    return [u for u in urls if "duckduckgo.com" not in u]


async def discover_product_url(brand: str, product: str) -> str:
    """
    Find the brand's own product page URL by searching DuckDuckGo.
    Falls back to SerpAPI if SERPAPI_KEY is set.
    Returns the first non-marketplace URL matching the brand domain.
    """
    from app.config import settings

    slug = _brand_slug(brand)
    query = f'"{brand}" {product}'

    if settings.serpapi_key:
        return await _serpapi_search(query, slug, settings.serpapi_key)

    return await _ddg_search(query, slug)


async def _ddg_search(query: str, brand_slug: str) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    params = {"q": query, "kl": "us-en"}
    async with httpx.AsyncClient(follow_redirects=True, timeout=15) as client:
        resp = await client.post(
            "https://html.duckduckgo.com/html/",
            data=params,
            headers=headers,
        )
        resp.raise_for_status()

    urls = _extract_urls_from_ddg(resp.text)

    # Prefer URLs whose domain contains the brand slug
    brand_urls = [u for u in urls if brand_slug in urlparse(u).netloc.lower()]
    non_marketplace = [u for u in brand_urls if not _is_marketplace(u)]

    if non_marketplace:
        return non_marketplace[0]

    # Fallback: first non-marketplace result
    fallback = [u for u in urls if not _is_marketplace(u)]
    if fallback:
        return fallback[0]

    raise RuntimeError(
        f"Could not discover a product page for '{query}'. "
        "Try providing a more specific brand name."
    )


async def _serpapi_search(query: str, brand_slug: str, api_key: str) -> str:
    params = {
        "q": query,
        "api_key": api_key,
        "engine": "google",
        "num": 10,
    }
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(
            "https://serpapi.com/search.json",
            params=params,
        )
        resp.raise_for_status()
        data = resp.json()

    results = data.get("organic_results", [])
    urls = [r.get("link", "") for r in results if r.get("link")]

    brand_urls = [u for u in urls if brand_slug in urlparse(u).netloc.lower()]
    non_marketplace = [u for u in brand_urls if not _is_marketplace(u)]

    if non_marketplace:
        return non_marketplace[0]

    fallback = [u for u in urls if not _is_marketplace(u)]
    if fallback:
        return fallback[0]

    raise RuntimeError(f"SerpAPI returned no usable results for '{query}'.")
