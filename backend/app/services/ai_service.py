import json
import re
from urllib.parse import urlparse
from typing import List

from app.core.config import settings
from app.schemas import TestStep
from app.services.llm_service import LLMUnavailable, chat_json, llm_status


def _domain_name(target_url: str) -> str:
    host = urlparse(target_url).netloc.replace("www.", "")
    return host.split(":")[0] or "website"


def _page_label(target_url: str, title: str) -> str:
    if title and len(title) <= 36:
        return title
    domain = _domain_name(target_url).split(".")[0]
    return domain.replace("-", " ").title() or "Website"


def _title_from_requirement(target_url: str, requirement: str, page_context: dict) -> str:
    if requirement.strip():
        words = re.findall(r"[A-Za-z0-9]+", requirement)[:8]
        return (" ".join(words).strip() or "Generated web test")[:80]
    title = page_context.get("title") or _domain_name(target_url)
    return f"Auto exploratory test for {title}"[:80]


def inspect_page(target_url: str) -> dict:
    """Collect a small page summary so generated tests are site-specific."""
    context = {
        "title": "",
        "inputs": [],
        "buttons": [],
        "links": [],
        "headings": [],
        "media": [],
        "error": "",
    }
    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        context["error"] = f"Playwright unavailable during inspection: {exc}"
        return context

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=settings.playwright_headless)
            page = browser.new_page()
            page.set_default_timeout(6000)
            page.goto(target_url, wait_until="domcontentloaded", timeout=12000)
            page.wait_for_timeout(1200)
            context["title"] = page.title()
            context.update(
                page.evaluate(
                    """() => {
                      const clean = value => String(value || '').replace(/\\s+/g, ' ').trim().slice(0, 90);
                      const selectorFor = el => {
                        if (el.id) return `#${CSS.escape(el.id)}`;
                        if (el.name) return `${el.tagName.toLowerCase()}[name="${CSS.escape(el.name)}"]`;
                        if (el.getAttribute('placeholder')) return `${el.tagName.toLowerCase()}[placeholder="${CSS.escape(el.getAttribute('placeholder'))}"]`;
                        if (el.type) return `${el.tagName.toLowerCase()}[type="${CSS.escape(el.type)}"]`;
                        return el.tagName.toLowerCase();
                      };
                      const visible = el => {
                        const rect = el.getBoundingClientRect();
                        const style = window.getComputedStyle(el);
                        return rect.width > 2 && rect.height > 2 && style.visibility !== 'hidden' && style.display !== 'none';
                      };
                      return {
                        inputs: Array.from(document.querySelectorAll('input, textarea'))
                          .filter(visible)
                          .slice(0, 8)
                          .map(el => ({
                            selector: selectorFor(el),
                            type: clean(el.type || el.tagName),
                            name: clean(el.name),
                            placeholder: clean(el.getAttribute('placeholder') || el.getAttribute('aria-label')),
                          })),
                        buttons: Array.from(document.querySelectorAll('button, input[type=submit], [role=button]'))
                          .filter(visible)
                          .slice(0, 8)
                          .map(el => ({
                            selector: selectorFor(el),
                            text: clean(el.innerText || el.value || el.getAttribute('aria-label')),
                          })),
                        links: Array.from(document.querySelectorAll('a[href]'))
                          .filter(visible)
                          .slice(0, 12)
                          .map(el => ({
                            selector: selectorFor(el),
                            text: clean(el.innerText || el.getAttribute('aria-label')),
                            href: el.href,
                          })),
                        headings: Array.from(document.querySelectorAll('h1, h2, h3'))
                          .filter(visible)
                          .slice(0, 8)
                          .map(el => clean(el.innerText))
                          .filter(Boolean),
                        media: Array.from(document.querySelectorAll('video, audio, img'))
                          .filter(visible)
                          .slice(0, 8)
                          .map(el => ({
                            selector: selectorFor(el),
                            type: el.tagName.toLowerCase(),
                            label: clean(el.getAttribute('alt') || el.getAttribute('aria-label')),
                          })),
                      };
                    }"""
                )
            )
            browser.close()
    except Exception as exc:
        context["error"] = f"Page inspection skipped: {type(exc).__name__}: {exc}"
    return context


def _search_keyword(requirement: str, target_url: str) -> str:
    quoted = re.search(r"['\"]([^'\"]+)['\"]", requirement)
    if quoted and re.search(r"search", requirement, re.I):
        return quoted.group(1).strip()[:80]

    match = re.search(
        r"(?:search(?:ing)?(?:\s+(?:for|about))?|find|look\s+for)\s+(?:a\s+|an\s+|the\s+)?(.+)",
        requirement,
        re.I,
    )
    if match:
        keyword = re.split(
            (
                r"\s*(?:,|;)?\s+(?:"
                r"and\s+(?:see|verify|check|confirm|ensure|make sure|open|click|select|play)"
                r"|then(?:\s+(?:open|click|select|verify|check|confirm|play))?"
                r"|after\s+(?:that|searching)"
                r"|so\s+(?:that|I|we|you)"
                r"|to\s+(?:verify|check|confirm|ensure|see)"
                r")\b"
            ),
            match.group(1),
            maxsplit=1,
            flags=re.I,
        )[0]
        keyword = re.sub(r"\s+(?:on|in)\s+(?:youtube|the website|the site)\s*$", "", keyword, flags=re.I)
        keyword = re.sub(
            r"\s+(?:and\s+)?(?:see|verify|check|confirm)\s+(?:the\s+)?expected\s+(?:output|result)s?.*$",
            "",
            keyword,
            flags=re.I,
        )
        return keyword.strip(" .?!,'\"")[:80]
    domain = _domain_name(target_url).split(".")[0]
    if "youtube" in domain:
        return "playwright test automation"
    return "test automation"


def _best_search_input(page_context: dict) -> dict:
    for item in page_context.get("inputs", []):
        blob = " ".join(str(item.get(key, "")) for key in ("type", "name", "placeholder")).lower()
        if "search" in blob or item.get("type") == "search":
            return item
    return {}


def _prompt_login_case(target_url: str, requirement: str, page_context: dict) -> dict:
    if not re.search(r"\b(?:sign in|signin|log in|login)\b", requirement, re.I):
        return {}
    if re.search(
        r"\b(?:without|do not|don't|dont|never|avoid)\b.{0,35}\b(?:sign in|signin|log in|login)\b",
        requirement,
        re.I,
    ):
        return {}

    page_name = page_context.get("title") or _domain_name(target_url)
    case_label = _page_label(target_url, page_name)
    domain = _domain_name(target_url).lower()
    dummy_email = "invalid.test.account@example.invalid"

    if "youtube" in domain:
        steps = [
            TestStep(action="goto", value=target_url, description="Open YouTube."),
            TestStep(
                action="assert_visible",
                selector="a[aria-label*='Sign in'], ytd-button-renderer a[href*='accounts.google.com']",
                description="Verify the YouTube Sign in control is visible.",
            ),
            TestStep(
                action="click",
                selector="a[aria-label*='Sign in'], ytd-button-renderer a[href*='accounts.google.com']",
                description="Open the Google authentication page.",
            ),
            TestStep(action="wait", value="1800", description="Wait for the authentication page to load."),
            TestStep(
                action="assert_url_contains",
                value="accounts.google.com",
                description="Verify YouTube redirected to Google authentication.",
            ),
            TestStep(
                action="assert_visible",
                selector="#identifierId, input[type='email']",
                description="Verify the account identifier field is visible.",
            ),
            TestStep(
                action="fill",
                selector="#identifierId, input[type='email']",
                value=dummy_email,
                description=f"Enter the deliberately invalid test account: {dummy_email}.",
            ),
            TestStep(
                action="assert_value",
                selector="#identifierId, input[type='email']",
                value=dummy_email,
                description="Confirm the invalid account identifier was entered correctly.",
            ),
            TestStep(action="screenshot", description="Capture the authentication form before submission."),
            TestStep(
                action="click",
                selector="#identifierNext button, #identifierNext",
                description="Submit the invalid account identifier.",
            ),
            TestStep(action="wait", value="1800", description="Wait for Google to validate the account."),
            TestStep(
                action="assert_url_contains",
                value="accounts.google.com",
                description="Verify authentication did not return to an authenticated YouTube session.",
            ),
            TestStep(
                action="assert_visible",
                selector="text=/couldn.?t find your google account|enter a valid email|browser or app may not be secure/i",
                description="Verify Google displays an authentication rejection message.",
            ),
            TestStep(action="screenshot", description="Capture the rejected sign-in state."),
        ]
        return {
            "name": "Verify YouTube rejects invalid sign-in credentials",
            "target_url": target_url,
            "requirement": requirement,
            "steps": steps,
            "expected_result": "YouTube redirects to Google authentication and the deliberately invalid account is not authenticated.",
        }

    email_input = next(
        (
            item
            for item in page_context.get("inputs", [])
            if any(
                token in " ".join(str(item.get(key, "")) for key in ("type", "name", "placeholder")).lower()
                for token in ("email", "user", "login")
            )
        ),
        {},
    )
    password_input = next(
        (item for item in page_context.get("inputs", []) if item.get("type") == "password"),
        {},
    )
    if not email_input or not password_input:
        return {}

    return {
        "name": f"Verify {page_name} rejects invalid sign-in credentials",
        "target_url": target_url,
        "requirement": requirement,
        "steps": [
            TestStep(action="goto", value=target_url, description="Open the target website."),
            TestStep(action="assert_visible", selector=email_input["selector"], description="Verify the account field is visible."),
            TestStep(action="fill", selector=email_input["selector"], value=dummy_email, description="Enter an invalid test account."),
            TestStep(action="assert_visible", selector=password_input["selector"], description="Verify the password field is visible."),
            TestStep(action="fill", selector=password_input["selector"], value="InvalidPassword123!", description="Enter an invalid test password."),
            TestStep(action="screenshot", description="Capture the invalid credentials before submission."),
            TestStep(
                action="click",
                selector="button[type='submit'], input[type='submit']",
                description="Submit the invalid credentials.",
            ),
            TestStep(action="wait", value="1500", description="Wait for authentication validation."),
            TestStep(action="assert_visible", selector=email_input["selector"], description="Verify the login form remains visible after rejection."),
            TestStep(action="screenshot", description="Capture the rejected login state."),
        ],
        "expected_result": "The invalid credentials are rejected and no authenticated session is created.",
    }


def _prompt_search_case(target_url: str, requirement: str, page_context: dict) -> dict:
    search_input = _best_search_input(page_context)
    if not search_input or not re.search(r"\b(?:search(?:ing)?|find|look for)\b", requirement, re.I):
        return {}

    keyword = _search_keyword(requirement, target_url)
    if not keyword:
        return {}

    selector = search_input.get("selector") or "input[type='search']"
    page_name = page_context.get("title") or _domain_name(target_url)
    domain = _domain_name(target_url).lower()
    steps = [
        TestStep(action="goto", value=target_url, description="Open the target website."),
        TestStep(action="assert_visible", selector=selector, description="Verify the search input is visible."),
        TestStep(action="fill", selector=selector, value=keyword, description=f"Enter the exact requested search phrase: {keyword}."),
        TestStep(action="assert_value", selector=selector, value=keyword, description=f"Confirm the search input contains exactly: {keyword}."),
        TestStep(action="screenshot", description="Capture the completed search input."),
        TestStep(action="press", selector=selector, value="Enter", description="Submit the search."),
        TestStep(action="wait", value="2500", description="Wait for search results to load."),
    ]

    should_open_result = bool(
        re.search(r"\b(?:open|click|select|play|watch)\b", requirement, re.I)
    )

    if "youtube" in domain:
        result_selector = "ytd-video-renderer a#video-title, ytd-rich-item-renderer a#video-title"
        steps.extend(
            [
                TestStep(action="assert_url_contains", value="search_query=", description="Verify YouTube opened a search results URL."),
                TestStep(action="assert_visible", selector=result_selector, description="Verify at least one video result is visible."),
                TestStep(action="assert_count", selector=result_selector, value="1", description="Verify the search returned one or more video results."),
                TestStep(action="assert_text", value=keyword, description=f"Verify the results page reflects the requested topic: {keyword}.", optional=True),
                TestStep(action="screenshot", description="Capture the YouTube search results."),
            ]
        )
        if should_open_result:
            steps.extend(
                [
                    TestStep(action="click", selector=result_selector, description="Open the first visible video result."),
                    TestStep(action="wait", value="2500", description="Wait for the selected video page to load."),
                    TestStep(action="assert_url_contains", value="watch", description="Verify navigation reached a YouTube watch page."),
                    TestStep(action="assert_visible", selector="#movie_player, video", description="Verify the video player is visible."),
                    TestStep(action="assert_title", description="Verify the video page has a title."),
                    TestStep(action="screenshot", description="Capture the opened video page."),
                ]
            )
            expected = f"YouTube searches for '{keyword}', returns relevant results, and opens a playable video."
            name = f"Search YouTube for {keyword} and open a result"
        else:
            expected = f"YouTube searches for '{keyword}' and displays one or more relevant video results."
            name = f"Search YouTube for {keyword} and verify results"
    else:
        generic_results = "main a, [role='main'] a, article a, .result a, .search-result a"
        steps.extend(
            [
                TestStep(action="assert_url_changed", value=target_url, description="Verify submitting search changed the page or URL.", optional=True),
                TestStep(action="assert_visible", selector=generic_results, description="Verify a search result or result link is visible.", optional=True),
                TestStep(action="screenshot", description="Capture the search result page."),
            ]
        )
        expected = f"The website searches for the exact phrase '{keyword}' and displays a result state."
        name = f"Search {page_name} for {keyword}"

    return {
        "name": name[:80],
        "target_url": target_url,
        "requirement": requirement,
        "steps": steps,
        "expected_result": expected,
    }


def _prompt_youtube_quality_case(target_url: str, requirement: str, page_context: dict) -> dict:
    domain = _domain_name(target_url).lower()
    if "youtube" not in domain:
        return {}
    if not re.search(r"\b(?:quality|resolution|resolutions|1080p|720p|480p|360p)\b", requirement, re.I):
        return {}
    if not re.search(r"\b(?:toggle|change|switch|select|test|check|verify|all)\b", requirement, re.I):
        return {}

    search_input = _best_search_input(page_context)
    selector = search_input.get("selector") if search_input else 'input[name="search_query"]'
    keyword = "4k video test"
    result_selector = "ytd-video-renderer a#video-title, ytd-rich-item-renderer a#video-title"
    return {
        "name": "Verify YouTube video quality options can be changed",
        "target_url": target_url,
        "requirement": requirement,
        "steps": [
            TestStep(action="goto", value=target_url, description="Open YouTube."),
            TestStep(action="assert_visible", selector=selector, description="Verify the YouTube search input is visible."),
            TestStep(action="fill", selector=selector, value=keyword, description=f"Search for a sample video using: {keyword}."),
            TestStep(action="press", selector=selector, value="Enter", description="Submit the video search."),
            TestStep(action="wait", value="2500", description="Wait for video results to load."),
            TestStep(action="assert_visible", selector=result_selector, description="Verify at least one video result is visible."),
            TestStep(action="click", selector=result_selector, description="Open the first visible video result."),
            TestStep(action="wait", value="3500", description="Wait for the selected video page to load."),
            TestStep(action="assert_url_contains", value="watch", description="Verify a YouTube watch page opened."),
            TestStep(action="assert_visible", selector="#movie_player, video", description="Verify the video player is visible."),
            TestStep(action="screenshot", description="Capture the player before changing quality."),
            TestStep(action="youtube_cycle_quality", description="Open Settings > Quality and cycle through the visible resolution options."),
            TestStep(action="assert_visible", selector="#movie_player, video", description="Verify the player remains visible after changing quality."),
            TestStep(action="screenshot", description="Capture the player after quality changes."),
        ],
        "expected_result": "A YouTube video opens, visible quality/resolution options can be selected, and the player remains usable.",
        "generation_source": "fallback",
        "intent_summary": "Open a YouTube video and test the available quality/resolution options.",
    }


def _fallback_steps(target_url: str, requirement: str, page_context: dict) -> List[TestStep]:
    text = requirement.lower()
    steps = [
        TestStep(action="goto", value=target_url, description="Open the target website."),
        TestStep(action="screenshot", description="Capture the initial page state."),
    ]

    if "login" in text or "sign in" in text:
        steps.extend(
            [
                TestStep(action="fill", selector="input[type='email'], input[name*='email'], input[name*='user']", value="demo@example.com", description="Fill the username or email field if present."),
                TestStep(action="fill", selector="input[type='password']", value="Password@123", description="Fill the password field if present.", optional=True),
                TestStep(action="click", selector="button[type='submit'], input[type='submit'], text=/login|sign in/i", description="Submit the login form if present.", optional=True),
            ]
        )

    search_input = _best_search_input(page_context)
    wants_search = "search" in text or (not requirement.strip() and search_input)
    if wants_search and search_input:
        keyword = _search_keyword(requirement, target_url)
        selector = search_input.get("selector") or "input[type='search']"
        steps.extend(
            [
                TestStep(action="fill", selector=selector, value=keyword, description=f"Enter search keyword: {keyword}."),
                TestStep(action="press", selector=selector, value="Enter", description="Run the search."),
                TestStep(action="wait", value="2000", description="Wait for search results or page updates."),
            ]
        )

    form_inputs = [item for item in page_context.get("inputs", []) if item.get("selector")]
    if "contact" in text or "form" in text or (not requirement.strip() and form_inputs and not search_input):
        steps.extend(
            [
                TestStep(action="fill", selector=form_inputs[0]["selector"], value="Test User", description="Fill the first visible input field."),
            ]
        )
        if len(form_inputs) > 1:
            steps.append(TestStep(action="fill", selector=form_inputs[1]["selector"], value="Automated test message", description="Fill the second visible input field."))

    if not requirement.strip() and not search_input and page_context.get("links"):
        first_link = next((link for link in page_context["links"] if link.get("text")), page_context["links"][0])
        if first_link.get("text"):
            steps.append(TestStep(action="assert_text", value=first_link["text"], description=f"Verify visible navigation text: {first_link['text']}."))

    steps.extend(
        [
            TestStep(action="assert_title", description="Verify that the page title is available."),
            TestStep(action="screenshot", description="Capture the final page state."),
        ]
    )
    return steps


def _case(name: str, target_url: str, steps: List[TestStep], expected_result: str, generation_source: str = "workflow-catalog") -> dict:
    return {
        "name": name[:80],
        "target_url": target_url,
        "requirement": "Generated from detected website workflows.",
        "steps": steps,
        "expected_result": expected_result,
        "generation_source": generation_source,
    }


def _wants_comprehensive_suite(requirement: str) -> bool:
    return not requirement.strip() or bool(
        re.search(
            r"\b(?:all|complete|comprehensive|full|major|possible|unique|end[- ]to[- ]end|functional)\b",
            requirement,
            re.I,
        )
    )


def _is_search_like_input(item: dict) -> bool:
    blob = " ".join(str(item.get(key, "")) for key in ("type", "name", "placeholder", "selector")).lower()
    return "search" in blob or item.get("type") == "search"


def _site_kind(target_url: str, page_context: dict) -> str:
    domain = _domain_name(target_url).lower()
    text = " ".join(
        [domain, page_context.get("title") or ""]
        + [button.get("text") or "" for button in page_context.get("buttons", [])]
        + [link.get("text") or "" for link in page_context.get("links", [])]
    ).lower()
    if any(token in domain for token in ("youtube", "vimeo", "netflix", "hotstar", "primevideo")):
        return "media"
    if any(token in text for token in ("cart", "wishlist", "product", "add to cart", "flipkart", "amazon")):
        return "ecommerce"
    if page_context.get("media"):
        return "media"
    return "general"


def _safe_form_inputs(page_context: dict) -> list:
    return [
        item
        for item in page_context.get("inputs", [])
        if item.get("selector")
        and item.get("type") not in ("hidden", "submit", "password")
        and not _is_search_like_input(item)
    ]


def _suite_page_availability(case_label: str, target_url: str) -> dict:
    return _case(
        f"{case_label} - page availability",
        target_url,
        [
            TestStep(action="goto", value=target_url, description="Open the target website."),
            TestStep(action="assert_title", description="Verify the page exposes a non-empty title."),
            TestStep(action="screenshot", description="Capture the loaded home page."),
        ],
        "The website loads, has a title, and produces visual evidence.",
    )


def _suite_search(case_label: str, target_url: str, page_context: dict, open_result: bool = False) -> dict:
    search_input = _best_search_input(page_context)
    keyword = _search_keyword("", target_url)
    selector = search_input.get("selector") or "input[type='search']"
    domain = _domain_name(target_url).lower()
    steps = [
        TestStep(action="goto", value=target_url, description="Open the target website."),
        TestStep(action="assert_visible", selector=selector, description="Verify the search input is visible."),
        TestStep(action="fill", selector=selector, value=keyword, description=f"Enter the search phrase: {keyword}."),
        TestStep(action="assert_value", selector=selector, value=keyword, description="Confirm the search phrase was entered."),
        TestStep(action="press", selector=selector, value="Enter", description="Submit the search."),
        TestStep(action="wait", value="2200", description="Wait for search results."),
    ]
    if "youtube" in domain:
        result_selector = "ytd-video-renderer a#video-title, ytd-rich-item-renderer a#video-title"
        steps.extend(
            [
                TestStep(action="assert_url_contains", value="search_query=", description="Verify YouTube opened a search results URL."),
                TestStep(action="assert_visible", selector=result_selector, description="Verify at least one video result is visible."),
            ]
        )
        if open_result:
            steps.extend(
                [
                    TestStep(action="click", selector=result_selector, description="Open the first visible video result."),
                    TestStep(action="wait", value="2500", description="Wait for the video page."),
                    TestStep(action="assert_url_contains", value="watch", description="Verify the watch page opened."),
                    TestStep(action="assert_visible", selector="#movie_player, video", description="Verify the video player is visible."),
                ]
            )
    else:
        steps.extend(
            [
                TestStep(action="assert_url_changed", value=target_url, description="Confirm the search changed the current page.", optional=True),
                TestStep(action="assert_visible", selector="main a, [role='main'] a, article a, .result a, .search-result a", description="Verify a result link or result area is visible.", optional=True),
            ]
        )
    steps.append(TestStep(action="screenshot", description="Capture the search result state."))
    return _case(
        f"{case_label} - {'video playback search' if open_result else 'search results'}",
        target_url,
        steps,
        "Search accepts input and reaches an observable result state."
        if not open_result
        else "Search finds media content and opens a playable result.",
    )


def _suite_ecommerce(case_label: str, target_url: str, page_context: dict) -> dict:
    search_input = _best_search_input(page_context)
    selector = search_input.get("selector") or "input[type='search'], input[placeholder*='Search' i]"
    add_cart_selector = (
        "button:has-text('Add to cart'), button:has-text('Add to Cart'), "
        "[role='button']:has-text('Add to cart'), [role='button']:has-text('ADD TO CART')"
    )
    return _case(
        f"{case_label} - product discovery",
        target_url,
        [
            TestStep(action="goto", value=target_url, description="Open the shopping website."),
            TestStep(action="assert_visible", selector=selector, description="Verify product search is available."),
            TestStep(action="fill", selector=selector, value="laptop", description="Search for a safe sample product."),
            TestStep(action="press", selector=selector, value="Enter", description="Submit the product search."),
            TestStep(action="wait", value="2500", description="Wait for product results."),
            TestStep(action="assert_url_changed", value=target_url, description="Verify the page moved to a product result state.", optional=True),
            TestStep(action="assert_visible", selector="a[href*='/p/'], [data-testid*='product'], .product, main a", description="Verify product results are visible.", optional=True),
            TestStep(action="assert_visible", selector=add_cart_selector, description="Check whether an add-to-cart control is available without checking out.", optional=True),
            TestStep(action="screenshot", description="Capture the product discovery result."),
        ],
        "A product can be searched and product discovery is verified without checkout or payment.",
    )


def _suite_media(case_label: str, target_url: str, page_context: dict) -> dict:
    domain = _domain_name(target_url).lower()
    if "youtube" in domain and _best_search_input(page_context):
        return _suite_search(case_label, target_url, page_context, open_result=True)
    # Limit playback discovery to interactive controls. A generic aria-label
    # selector also matches hidden containers such as "Video Player".
    playable_selector = "video, audio, button[aria-label*='play' i], [role='button'][aria-label*='play' i], button:has-text('Play'), [role='button']:has-text('Play')"
    playback_or_access_selector = "video, audio, button[aria-label*='pause' i], [role='button'][aria-label*='pause' i], button[aria-label*='play' i], [role='button'][aria-label*='play' i], button:has-text('Play'), a:has-text('Sign in'), button:has-text('Sign in'), [role='button']:has-text('Sign in')"
    return _case(
        f"{case_label} - media playback entry point",
        target_url,
        [
            TestStep(action="goto", value=target_url, description="Open the media website."),
            TestStep(action="assert_title", description="Verify the media website loaded."),
            TestStep(action="assert_visible", selector=playable_selector, description="Verify a video, audio, or play control is available.", optional=True),
            TestStep(action="screenshot", description="Capture the media entry point before interaction."),
            TestStep(action="click", selector=playable_selector, description="Activate the visible play control if it is available.", optional=True),
            TestStep(action="wait", value="1500", description="Wait for the player or page response."),
            TestStep(action="assert_visible", selector=playback_or_access_selector, description="Verify the player remains visible or safely requires sign-in.", optional=True),
            TestStep(action="screenshot", description="Capture the media playback entry point."),
        ],
        "The website exposes a safe media playback entry point or shows that playback requires sign-in.",
    )


def _suite_auth_guardrail(case_label: str, target_url: str, page_context: dict) -> dict:
    login = next(
        (
            item
            for item in page_context.get("links", []) + page_context.get("buttons", [])
            if item.get("selector") and re.search(r"\b(login|sign in|sign-in)\b", item.get("text") or "", re.I)
        ),
        {},
    )
    if not login:
        return {}
    label = login.get("text") or "sign in"
    return _case(
        f"{case_label} - sign-in guardrail",
        target_url,
        [
            TestStep(action="goto", value=target_url, description="Open the target website."),
            TestStep(action="assert_visible", selector=login["selector"], description=f"Verify the {label} entry point is visible."),
            TestStep(action="click", selector=login["selector"], description=f"Open the {label} entry point.", optional=True),
            TestStep(action="wait", value="1500", description="Wait for the authentication screen."),
            TestStep(action="assert_title", description="Verify the authentication flow opened a valid page."),
            TestStep(action="assert_visible", selector="input[type='email'], input[name*='email'], input[name*='user'], input[type='tel']", description="Verify an account identifier field is available if the sign-in form is shown.", optional=True),
            TestStep(action="fill", selector="input[type='email'], input[name*='email'], input[name*='user'], input[type='tel']", value="invalid.test.account@example.invalid", description="Enter a deliberately invalid test account only if the field is visible.", optional=True),
            TestStep(action="assert_value", selector="input[type='email'], input[name*='email'], input[name*='user'], input[type='tel']", value="invalid.test.account@example.invalid", description="Confirm the invalid test account was entered.", optional=True),
            TestStep(action="screenshot", description="Capture the unauthenticated sign-in state."),
        ],
        "The authentication entry point is reachable and can be checked safely without real credentials.",
    )


def _suite_primary_action(case_label: str, target_url: str, page_context: dict) -> dict:
    cta = next(
        (
            item
            for item in page_context.get("buttons", []) + page_context.get("links", [])
            if item.get("selector")
            and re.search(r"\b(get started|start|join|subscribe|try|watch|shop|explore|learn more)\b", item.get("text") or "", re.I)
        ),
        {},
    )
    email_input = next(
        (
            item
            for item in page_context.get("inputs", [])
            if item.get("selector") and re.search(r"email", " ".join(str(item.get(k, "")) for k in ("type", "name", "placeholder")), re.I)
        ),
        {},
    )
    if not cta and not email_input:
        return {}
    label = cta.get("text") or "primary action"
    steps = [
        TestStep(action="goto", value=target_url, description="Open the website landing page."),
        TestStep(action="assert_title", description="Verify the landing page loaded."),
    ]
    if email_input:
        steps.extend(
            [
                TestStep(action="assert_visible", selector=email_input["selector"], description="Verify the email or account-start field is visible."),
                TestStep(action="fill", selector=email_input["selector"], value="invalid.test.account@example.invalid", description="Enter a safe invalid test email."),
                TestStep(action="assert_value", selector=email_input["selector"], value="invalid.test.account@example.invalid", description="Confirm the test email was entered."),
            ]
        )
    if cta:
        steps.extend(
            [
                TestStep(action="assert_visible", selector=cta["selector"], description=f"Verify the primary action is visible: {label}."),
                TestStep(action="click", selector=cta["selector"], description=f"Activate the primary action: {label}.", optional=True),
                TestStep(action="wait", value="1500", description="Wait for the page response."),
                TestStep(action="assert_title", description="Verify the destination remains a valid page."),
            ]
        )
    steps.append(TestStep(action="screenshot", description="Capture the primary action result."))
    return _case(
        f"{case_label} - primary user journey",
        target_url,
        steps,
        "The main call-to-action or account-start journey is reachable and behaves safely with test data.",
    )


def _suite_content_navigation(case_label: str, target_url: str, page_context: dict) -> dict:
    link = _safe_link(page_context, target_url)
    if not link:
        return {}
    text = link.get("text") or "content link"
    return _case(
        f"{case_label} - content navigation journey",
        target_url,
        [
            TestStep(action="goto", value=target_url, description="Open the target website."),
            TestStep(action="assert_title", description="Verify the starting page loaded."),
            TestStep(action="assert_text", value=text, description=f"Verify the navigation item is visible: {text}."),
            TestStep(action="screenshot", description="Capture the navigation item before opening it."),
            TestStep(action="click", selector=link["selector"], description=f"Open the navigation item: {text}.", optional=True),
            TestStep(action="wait", value="1500", description="Wait for navigation or content update."),
            TestStep(action="assert_title", description="Verify the destination has a valid title."),
            TestStep(action="screenshot", description="Capture the destination or updated content."),
        ],
        "A meaningful content/navigation path can be opened and verified with visual evidence.",
    )


def _suite_media_asset(case_label: str, target_url: str, page_context: dict) -> dict:
    media = page_context.get("media", [])
    if not media:
        return {}
    item = media[0]
    return _case(
        f"{case_label} - media asset visibility",
        target_url,
        [
            TestStep(action="goto", value=target_url, description="Open the target website."),
            TestStep(action="assert_title", description="Verify the page loaded."),
            TestStep(action="assert_visible", selector=item["selector"], description=f"Verify visible {item['type']} media is rendered."),
            TestStep(action="wait", value="800", description="Allow lazy-loaded media to settle."),
            TestStep(action="assert_visible", selector=item["selector"], description="Verify the media remains visible after settling."),
            TestStep(action="screenshot", description="Capture the rendered media evidence."),
        ],
        "Important media content renders and remains visible after the page settles.",
    )


def _safe_button(page_context: dict) -> dict:
    preferred_words = ("menu", "guide", "more", "settings", "navigation", "explore")
    blocked_words = ("sign in", "login", "buy", "purchase", "delete", "remove", "submit", "pay")
    buttons = page_context.get("buttons", [])
    for button in buttons:
        text = (button.get("text") or "").lower()
        if text and any(word in text for word in preferred_words):
            return button
    for button in buttons:
        text = (button.get("text") or "").lower()
        if button.get("selector") and not any(word in text for word in blocked_words):
            return button
    return {}


def _safe_link(page_context: dict, target_url: str) -> dict:
    target_host = urlparse(target_url).netloc
    blocked_words = ("sign in", "login", "privacy", "terms", "help", "buy", "purchase")
    for link in page_context.get("links", []):
        text = (link.get("text") or "").strip()
        href = link.get("href") or ""
        if (
            text
            and link.get("selector")
            and urlparse(href).netloc == target_host
            and not any(word in text.lower() for word in blocked_words)
            and href.rstrip("/") != target_url.rstrip("/")
        ):
            return link
    return {}


def generate_test_suite(target_url: str, requirement: str = "") -> dict:
    """Create distinct safe test cases for major features detected on the page."""
    page_context = inspect_page(target_url)
    requirement = requirement.strip()
    comprehensive = _wants_comprehensive_suite(requirement)
    suite_requirement = requirement or (
        "Create a complete functional test suite for the detected website. "
        "Cover the safest important user workflows: page load, search, navigation, sign-in guardrail, "
        "media playback if present, ecommerce product discovery if present, and forms if present."
    )
    if llm_status().get("available"):
        try:
            return _suite_with_ai(target_url, suite_requirement, page_context)
        except (LLMUnavailable, ValueError, TypeError, KeyError):
            pass

    page_name = page_context.get("title") or _domain_name(target_url)
    case_label = _page_label(target_url, page_name)
    tests = []
    detected_features = []

    if not comprehensive:
        detected_features.append("page availability")
        tests.append(_suite_page_availability(case_label, target_url))

    primary_case = _suite_primary_action(case_label, target_url, page_context)
    if primary_case:
        detected_features.append("primary user journey")
        tests.append(primary_case)

    headings = page_context.get("headings", [])
    if headings and not comprehensive:
        detected_features.append("visible content")
        tests.append(
            _case(
                f"{case_label} - visible content",
                target_url,
                [
                    TestStep(action="goto", value=target_url, description="Open the target website."),
                    TestStep(action="assert_text", value=headings[0], description=f"Verify the main visible heading: {headings[0]}."),
                    TestStep(action="screenshot", description="Capture the verified content."),
                ],
                "Important visible page content is rendered.",
            )
        )

    search_input = _best_search_input(page_context)
    if search_input:
        detected_features.append("search")
        tests.append(_suite_search(case_label, target_url, page_context))

    kind = _site_kind(target_url, page_context)
    if kind == "ecommerce" and search_input:
        detected_features.append("ecommerce product discovery")
        tests.append(_suite_ecommerce(case_label, target_url, page_context))

    if kind == "media":
        detected_features.append("media workflow")
        tests.append(_suite_media(case_label, target_url, page_context))

    auth_case = _suite_auth_guardrail(case_label, target_url, page_context)
    if auth_case:
        detected_features.append("authentication entry point")
        tests.append(auth_case)

    form_inputs = _safe_form_inputs(page_context)
    if form_inputs:
        detected_features.append("form inputs")
        form_steps = [
            TestStep(action="goto", value=target_url, description="Open the target website."),
            TestStep(action="assert_title", description="Verify the form page loaded."),
            TestStep(action="assert_visible", selector=form_inputs[0]["selector"], description="Verify the first form input is visible."),
            TestStep(action="fill", selector=form_inputs[0]["selector"], value="Automated Test User", description="Enter safe sample data in the first form field."),
            TestStep(action="assert_value", selector=form_inputs[0]["selector"], value="Automated Test User", description="Confirm the first form field kept the entered value."),
        ]
        if len(form_inputs) > 1:
            form_steps.extend(
                [
                    TestStep(action="assert_visible", selector=form_inputs[1]["selector"], description="Verify the second form input is visible."),
                    TestStep(action="fill", selector=form_inputs[1]["selector"], value="automated.test@example.com", description="Enter safe sample data in the second form field."),
                    TestStep(action="assert_value", selector=form_inputs[1]["selector"], value="automated.test@example.com", description="Confirm the second form field kept the entered value."),
                ]
            )
        form_steps.extend(
            [
                TestStep(action="wait", value="500", description="Wait for client-side validation or formatting."),
                TestStep(action="screenshot", description="Capture the completed form state without submitting it."),
            ]
        )
        tests.append(
            _case(
                f"{case_label} - form input validation",
                target_url,
                form_steps,
                "Visible form fields accept and retain safe sample data without submitting the form.",
            )
        )

    navigation_case = _suite_content_navigation(case_label, target_url, page_context)
    if navigation_case:
        detected_features.append("navigation")
        tests.append(navigation_case)

    button = _safe_button(page_context)
    if button:
        detected_features.append("interactive controls")
        button_name = button.get("text") or "page control"
        tests.append(
            _case(
                f"{case_label} - interactive control",
                target_url,
                [
                    TestStep(action="goto", value=target_url, description="Open the target website."),
                    TestStep(action="assert_title", description="Verify the starting page loaded."),
                    TestStep(action="assert_visible", selector=button["selector"], description=f"Verify the control is visible: {button_name}."),
                    TestStep(action="screenshot", description="Capture the control before activation."),
                    TestStep(action="click", selector=button["selector"], description=f"Activate the control: {button_name}.", optional=True),
                    TestStep(action="wait", value="800", description="Wait for the interface response."),
                    TestStep(action="assert_title", description="Verify the page remains usable after activation."),
                    TestStep(action="screenshot", description="Capture the interface after interaction."),
                ],
                "A safe visible control responds to user interaction.",
            )
        )

    media_case = _suite_media_asset(case_label, target_url, page_context)
    if media_case:
        detected_features.append("media rendering")
        tests.append(media_case)

    if not tests:
        detected_features.append("page availability")
        tests.append(_suite_page_availability(case_label, target_url))

    return {
        "target_url": target_url,
        "page_title": page_name,
        "detected_features": list(dict.fromkeys(detected_features)),
        "tests": tests,
    }


SUPPORTED_ACTIONS = {
    "goto",
    "click",
    "fill",
    "press",
    "assert_text",
    "assert_visible",
    "assert_title",
    "assert_url_changed",
    "assert_url_contains",
    "assert_value",
    "assert_count",
    "screenshot",
    "wait",
    "youtube_cycle_quality",
}


def is_suite_request(requirement: str) -> bool:
    return bool(
        re.search(
            (
                r"\b(?:all|complete|comprehensive|full|major|multiple)\b.{0,30}"
                r"\b(?:functional|functionality|test|tests|testing|test cases|suite)\b"
                r"|\b(?:test|cover|validate)\s+(?:all|everything|the whole|every)\b"
                r"|\b(?:functional|regression|smoke|end[- ]to[- ]end)\s+(?:test\s+)?suite\b"
            ),
            requirement,
            re.I,
        )
    )


def _extract_intent_with_ai(target_url: str, requirement: str, page_context: dict) -> dict:
    system = """/no_think
You are a senior QA analyst. Interpret the user's natural-language web testing request.
Separate literal test data from instructions and expected behavior. Do not copy the whole sentence into test data.
Do not repeat the input JSON. Transform it into the exact output schema below.
The output object may contain ONLY these keys:
action, objective, test_data, requested_actions, expected_outcomes, safety_constraints, ambiguities.

Examples:
- "search for 8k video and verify expected results"
  -> action=search, search_query="8k video", expected=["relevant results are visible"]
- "search for cats then open the first video and verify it plays"
  -> action=search_and_open, search_query="cats", requested_actions=["open first result"], expected=["watch page opens", "player is visible"]
- "try dummy login and confirm it does not sign in"
  -> action=negative_login, credential_mode="deliberately_invalid", expected=["authentication is rejected"]

Return JSON only:
{
  "action": "short machine-readable action",
  "objective": "one sentence describing what the user wants tested",
  "test_data": {"search_query": "", "username": "", "other": {}},
  "requested_actions": ["ordered user actions"],
  "expected_outcomes": ["observable validations"],
  "safety_constraints": ["actions that must not be performed"],
  "ambiguities": []
}
"""
    user = "\n".join(
        [
            "Analyze this testing request and transform it into the required intent schema.",
            f"TARGET URL: {target_url}",
            f"PAGE TITLE: {page_context.get('title') or ''}",
            f"USER REQUEST: {requirement}",
            "VISIBLE INPUTS: " + json.dumps(page_context.get("inputs", []), ensure_ascii=True),
            "VISIBLE BUTTONS: " + json.dumps(page_context.get("buttons", []), ensure_ascii=True),
            "VISIBLE LINKS: " + json.dumps(page_context.get("links", []), ensure_ascii=True),
            "Return the transformed intent JSON now. Do not repeat these labels.",
        ]
    )
    result = chat_json(system, user)
    required_keys = {"action", "objective", "test_data", "requested_actions", "expected_outcomes"}
    if not required_keys.issubset(result):
        raise ValueError(
            f"Qwen intent output did not follow the required schema; returned keys: {sorted(result.keys())}"
        )
    return result


def _suite_with_ai(target_url: str, requirement: str, page_context: dict) -> dict:
    system = f"""/no_think
You are a senior QA lead. Create a comprehensive functional test suite for the requested website.
Do not return one test. Return 5-10 distinct test cases covering different major user functions.
Use only these executable actions: {", ".join(sorted(SUPPORTED_ACTIONS))}.

Use the visible controls and page structure supplied by Playwright. Do not invent credentials,
submit purchases, place orders, delete data, or perform irreversible actions. Shopping/cart tests
may stop before checkout. Authentication tests must use deliberately invalid accounts.

Each case must include:
- a distinct behavioral objective
- precondition checks
- user interactions
- observable assertions
- final evidence screenshot

Return JSON only with exactly these keys:
{{
  "page_title": "website name",
  "detected_features": ["feature names"],
  "tests": [
    {{
      "name": "distinct test name",
      "intent_summary": "what this case verifies",
      "expected_result": "observable expected outcome",
      "test_data": {{"search_query": "", "other": {{}}}},
      "steps": [
        {{"action":"...", "selector":null, "value":null, "description":"...", "optional":false}}
      ]
    }}
  ]
}}
"""
    user = "\n".join(
        [
            "Build a multi-case suite from this request.",
            f"TARGET URL: {target_url}",
            f"USER REQUEST: {requirement}",
            f"PAGE TITLE: {page_context.get('title') or ''}",
            "VISIBLE INPUTS: " + json.dumps(page_context.get("inputs", []), ensure_ascii=True),
            "VISIBLE BUTTONS: " + json.dumps(page_context.get("buttons", []), ensure_ascii=True),
            "VISIBLE LINKS: " + json.dumps(page_context.get("links", []), ensure_ascii=True),
            "PAGE HEADINGS: " + json.dumps(page_context.get("headings", []), ensure_ascii=True),
            "VISIBLE MEDIA: " + json.dumps(page_context.get("media", []), ensure_ascii=True),
            "Return the suite JSON now. Do not repeat these labels.",
        ]
    )
    result = chat_json(system, user, num_predict=3500, timeout=120)
    if not {"page_title", "detected_features", "tests"}.issubset(result):
        raise ValueError(f"Qwen suite output returned invalid keys: {sorted(result.keys())}")

    raw_tests = result.get("tests") or []
    if not 5 <= len(raw_tests) <= 10:
        raise ValueError("Qwen suite must contain 5-10 distinct test cases.")

    generated_tests = []
    names = set()
    for raw_test in raw_tests:
        steps = []
        for raw_step in raw_test.get("steps", []):
            step_data = dict(raw_step)
            for field in ("action", "selector", "value", "description"):
                if step_data.get(field) is not None:
                    step_data[field] = str(step_data[field])
            step_data.setdefault("description", step_data.get("action") or "Execute test step.")
            steps.append(TestStep(**step_data))
        if any(step.action not in SUPPORTED_ACTIONS for step in steps):
            raise ValueError("Suite contains unsupported actions.")
        if len(steps) > 20:
            raise ValueError("Each suite case must contain no more than 20 steps.")

        name = str(raw_test.get("name") or "").strip()
        if not name or name.lower() in names:
            raise ValueError("Suite case names must be unique.")
        names.add(name.lower())

        intent = {
            "action": "suite_case",
            "test_data": raw_test.get("test_data") or {},
        }
        steps = _normalize_ai_steps(steps, intent, page_context, target_url)
        if not steps or steps[0].action != "goto":
            steps.insert(0, TestStep(action="goto", value=target_url, description="Open the target website."))
        if not any(step.action.startswith("assert_") for step in steps):
            steps.insert(1, TestStep(action="assert_title", description="Verify the destination page has a title."))
        if not any(step.action == "screenshot" for step in steps):
            steps.append(TestStep(action="screenshot", description="Capture final evidence for this test."))
        if len(steps) < 5:
            steps.insert(1, TestStep(action="assert_title", description="Verify the website loaded successfully."))
        if len(steps) < 5:
            steps.insert(2, TestStep(action="screenshot", description="Capture the initial page state."))
        if len(steps) < 5:
            steps.insert(-1, TestStep(action="wait", value="500", description="Wait for the interface to settle."))
        generated_tests.append(
            {
                "name": name,
                "target_url": target_url,
                "requirement": requirement,
                "steps": steps,
                "expected_result": raw_test.get("expected_result") or "The requested behavior is verified.",
                "generation_source": "qwen-ai",
                "intent_summary": raw_test.get("intent_summary") or name,
            }
        )

    return {
        "target_url": target_url,
        "page_title": result.get("page_title") or page_context.get("title") or _domain_name(target_url),
        "detected_features": result.get("detected_features") or [test["name"] for test in generated_tests],
        "tests": generated_tests,
    }


def _plan_with_ai(target_url: str, requirement: str, page_context: dict, intent: dict, feedback=None) -> dict:
    system = f"""/no_think
You are a senior Playwright test architect. Create one deep, executable test from the interpreted intent.
Do not repeat the input JSON. Return a new plan object.
The output object may contain ONLY these keys: name, intent_summary, expected_result, steps.

Supported actions only: {", ".join(sorted(SUPPORTED_ACTIONS))}.

Requirements:
- Follow the interpreted intent, not merely the original wording.
- Use literal test data only from intent.test_data.
- Use detected selectors where possible.
- Include precondition checks before interaction.
- Include assertions for every expected outcome.
- Include screenshots before important submission and after the final result.
- Do not submit purchases, delete data, or use real credentials.
- For negative login, use deliberately invalid data and verify rejection.
- Do not add actions the user did not request unless needed to reach or validate the requested state.
- Produce 8-20 meaningful steps for an interactive workflow.

Return JSON only:
{{
  "name": "concise behavioral test name",
  "intent_summary": "what you understood and will verify",
  "expected_result": "specific observable result",
  "steps": [
    {{"action":"...", "selector":null, "value":null, "description":"...", "optional":false}}
  ]
}}
"""
    user_parts = [
        "Build the executable test plan from this interpreted intent.",
        f"TARGET URL: {target_url}",
        f"ORIGINAL REQUEST: {requirement}",
        "INTERPRETED INTENT: " + json.dumps(intent, ensure_ascii=True),
        "VISIBLE INPUTS: " + json.dumps(page_context.get("inputs", []), ensure_ascii=True),
        "VISIBLE BUTTONS: " + json.dumps(page_context.get("buttons", []), ensure_ascii=True),
        "VISIBLE LINKS: " + json.dumps(page_context.get("links", []), ensure_ascii=True),
        "PAGE HEADINGS: " + json.dumps(page_context.get("headings", []), ensure_ascii=True),
        "Return the new plan JSON now. Do not repeat these labels.",
    ]
    if feedback:
        user_parts.append("CORRECTION FEEDBACK: " + json.dumps(feedback, ensure_ascii=True))
    result = chat_json(system, "\n".join(user_parts))
    if not {"name", "intent_summary", "expected_result", "steps"}.issubset(result):
        raise ValueError(
            f"Qwen plan output did not follow the required schema; returned keys: {sorted(result.keys())}"
        )
    return result


def _validate_ai_plan(plan: dict, intent: dict) -> tuple:
    errors = []
    raw_steps = plan.get("steps") or []
    try:
        steps = [TestStep(**step) for step in raw_steps]
    except (TypeError, ValueError) as exc:
        return [], [f"Invalid step schema: {exc}"]

    if not (8 <= len(steps) <= 20):
        errors.append("Interactive plans must contain 8-20 meaningful steps.")
    unsupported = [step.action for step in steps if step.action not in SUPPORTED_ACTIONS]
    if unsupported:
        errors.append(f"Unsupported actions: {unsupported}")
    if not steps or steps[0].action != "goto":
        errors.append("The first step must open the target website.")
    if not any(step.action.startswith("assert_") for step in steps):
        errors.append("The plan must validate an observable outcome.")
    if not any(step.action in {"click", "fill", "press"} for step in steps):
        errors.append("The plan must perform the requested interaction.")

    search_query = str((intent.get("test_data") or {}).get("search_query") or "").strip()
    if search_query:
        fill_values = [str(step.value or "").strip() for step in steps if step.action == "fill"]
        if search_query not in fill_values:
            errors.append(f"The exact interpreted search query '{search_query}' must be used in a fill step.")

    action = str(intent.get("action") or "").lower()
    if "login" in action:
        click_index = next((index for index, step in enumerate(steps) if step.action == "click"), None)
        fill_index = next((index for index, step in enumerate(steps) if step.action == "fill"), None)
        if click_index is None or fill_index is None or click_index > fill_index:
            errors.append("Login workflows must navigate to the authentication form before entering credentials.")

    return steps, errors


def _normalize_ai_steps(steps: List[TestStep], intent: dict, page_context: dict, target_url: str) -> List[TestStep]:
    """Repair mechanical action/selector mismatches without changing AI intent."""
    search_query = str((intent.get("test_data") or {}).get("search_query") or "").strip()
    search_input = _best_search_input(page_context)
    search_selector = search_input.get("selector") if search_input else ""
    domain = _domain_name(target_url).lower()
    youtube_result_selector = "ytd-video-renderer a#video-title, ytd-rich-item-renderer a#video-title"
    account_input = next(
        (
            item
            for item in page_context.get("inputs", [])
            if item.get("selector")
            and item.get("type") not in ("hidden", "password", "search")
            and item.get("name") != "q"
            and "search" not in str(item.get("placeholder") or "").lower()
        ),
        {},
    )
    password_input = next(
        (item for item in page_context.get("inputs", []) if item.get("type") == "password"),
        {},
    )
    auth_button = next(
        (
            button
            for button in page_context.get("buttons", [])
            if button.get("selector")
            and any(token in str(button.get("text") or "").lower() for token in ("login", "sign in", "otp"))
        ),
        {},
    )
    login_link = next(
        (
            link
            for link in page_context.get("links", [])
            if link.get("selector") and str(link.get("text") or "").strip().lower() in ("login", "sign in")
        ),
        {},
    )
    result_opened = False
    normalized = []

    for step in steps:
        data = step.model_dump()
        selector = str(step.selector or "")
        text_selector = re.fullmatch(
            r"[a-zA-Z][\w-]*\[text\s*=\s*(['\"])(.*?)\1\]",
            selector,
        )
        if text_selector:
            text_value = re.escape(text_selector.group(2)).replace(r"\/", "/")
            data["selector"] = f"text=/^{text_value}$/i"
        elif (
            step.action in {"click", "assert_visible"}
            and selector.strip().lower() in {"a", "button", "span", "div", "[role='button']", '[role="button"]'}
            and str(step.value or "").strip()
        ):
            text_value = re.escape(str(step.value).strip()).replace(r"\/", "/")
            data["selector"] = f"text=/^{text_value}$/i"

        if step.action == "goto" and not step.value:
            data["value"] = target_url

        description = step.description.lower()
        semantic_selector = f"{selector} {description}".lower()
        if (
            step.action == "click"
            and login_link
            and "login" in semantic_selector
            and any(token in semantic_selector for token in ("link", "navigate", "open", "page"))
        ):
            link_text = str(login_link.get("text") or "").strip()
            data["selector"] = f"text=/^{re.escape(link_text)}$/i"
        elif step.action == "fill" and any(
            token in semantic_selector for token in ("username", "email", "mobile", "phone", "account")
        ):
            if account_input:
                data["selector"] = account_input["selector"]
        elif step.action == "fill" and "password" in semantic_selector and not password_input:
            data["optional"] = True
        elif (
            step.action == "click"
            and auth_button
            and any(token in semantic_selector for token in ("submit", "otp", "authenticate"))
        ):
            button_text = str(auth_button.get("text") or "").strip()
            data["selector"] = f"text=/^{re.escape(button_text)}$/i"

        if search_query and search_selector:
            if step.action == "fill" and str(step.value or "").strip() == search_query:
                data["selector"] = search_selector
            elif step.action == "press" and str(step.value or "").lower() in ("enter", "return"):
                data["selector"] = search_selector
            elif (
                step.action in {"assert_text", "assert_visible"}
                and any(token in semantic_selector for token in ("search", "placeholder", "search box", "search input"))
            ):
                data["action"] = "assert_visible"
                data["selector"] = search_selector
                data["value"] = None

        if "youtube" in domain and search_query:
            if step.action in {"assert_count", "click"} and any(
                word in description for word in ("result", "video")
            ):
                data["selector"] = youtube_result_selector
                if step.action == "click":
                    result_opened = True
            elif (
                step.action == "assert_visible"
                and not result_opened
                and any(word in description for word in ("result", "video result"))
            ):
                data["selector"] = youtube_result_selector
            elif (
                step.action == "assert_visible"
                and result_opened
                and any(word in description for word in ("player", "video"))
            ):
                data["selector"] = "#movie_player, video"

        normalized.append(TestStep(**data))

    return normalized


def _ai_generated_case(target_url: str, requirement: str, page_context: dict) -> dict:
    intent = _extract_intent_with_ai(target_url, requirement, page_context)
    plan = _plan_with_ai(target_url, requirement, page_context, intent)
    steps, errors = _validate_ai_plan(plan, intent)
    steps = _normalize_ai_steps(steps, intent, page_context, target_url)

    if errors:
        plan = _plan_with_ai(
            target_url,
            requirement,
            page_context,
            intent,
            feedback={
                "validation_errors": errors,
                "previous_plan": plan,
                "instruction": "Correct every validation error without changing the interpreted intent.",
            },
        )
        steps, errors = _validate_ai_plan(plan, intent)
        steps = _normalize_ai_steps(steps, intent, page_context, target_url)

    if errors:
        raise ValueError("; ".join(errors))

    intent_summary = plan.get("intent_summary") or intent.get("objective") or requirement
    return {
        "name": plan.get("name") or _title_from_requirement(target_url, requirement, page_context),
        "target_url": target_url,
        "requirement": requirement,
        "steps": steps,
        "expected_result": plan.get("expected_result") or "; ".join(intent.get("expected_outcomes", [])),
        "generation_source": "qwen-ai",
        "intent_summary": intent_summary,
    }


def generate_test_case(target_url: str, requirement: str) -> dict:
    requirement = requirement.strip()
    page_context = inspect_page(target_url)

    # Ollama can be reachable while the configured model is not installed.
    # In that state, skip slow failed model calls and generate the deterministic
    # test case immediately.
    llm = llm_status()
    if requirement and llm.get("available") and llm.get("model_installed"):
        try:
            return _ai_generated_case(target_url, requirement, page_context)
        except (LLMUnavailable, ValueError, TypeError, KeyError):
            pass

    prompt_login_case = _prompt_login_case(target_url, requirement, page_context)
    if prompt_login_case:
        prompt_login_case["generation_source"] = "fallback"
        prompt_login_case["intent_summary"] = "Test invalid sign-in and verify that authentication is rejected."
        return prompt_login_case
    prompt_quality_case = _prompt_youtube_quality_case(target_url, requirement, page_context)
    if prompt_quality_case:
        return prompt_quality_case
    prompt_search_case = _prompt_search_case(target_url, requirement, page_context)
    if prompt_search_case:
        prompt_search_case["generation_source"] = "fallback"
        prompt_search_case["intent_summary"] = f"Search using the interpreted query '{_search_keyword(requirement, target_url)}' and validate the requested result state."
        return prompt_search_case

    # If the validated Qwen plan cannot be produced, use the deterministic
    # generator below. Avoiding a second, looser LLM attempt keeps plans stable.
    return {
        "name": _title_from_requirement(target_url, requirement, page_context),
        "target_url": target_url,
        "requirement": requirement,
        "steps": _fallback_steps(target_url, requirement, page_context),
        "expected_result": "The page loads, the requested workflow is attempted, and evidence is captured.",
        "generation_source": "fallback",
        "intent_summary": requirement or "Automatically inspect and exercise the detected page.",
    }
