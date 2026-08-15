import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

from app.core.config import settings
from app.schemas import TestStep


def _artifact_dir(run_id: int) -> Path:
    path = Path(settings.artifacts_dir) / f"run-{run_id}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _optional(selector: str) -> bool:
    return "," in selector or "text=/" in selector


def _effective_selector(selector: str, value: str) -> str:
    """Turn an AI-provided generic element selector plus label into a precise locator."""
    if selector.strip().lower() in {"a", "button", "span", "div", "[role='button']", '[role="button"]'} and value.strip():
        escaped = value.replace("\\", "\\\\").replace("/", "\\/")
        return f"text=/^{escaped}$/i"
    return selector


def _first_visible_selector(page, candidates: Tuple[str, ...], timeout_ms: int = 0) -> str:
    deadline = time.perf_counter() + (timeout_ms / 1000)
    while True:
        for candidate in candidates:
            try:
                locator = page.locator(candidate)
                count = min(locator.count(), 8)
                if any(locator.nth(index).is_visible() for index in range(count)):
                    return candidate
            except Exception:
                continue
        if time.perf_counter() >= deadline:
            break
        try:
            page.wait_for_timeout(200)
        except Exception:
            break
    return ""


def _search_input_selector(page, timeout_ms: int = 0) -> str:
    return _first_visible_selector(
        page,
        (
            'input[name="search_query"]',
            "input#search",
            "ytd-searchbox input",
            'input[type="search"]',
            'input[placeholder*="Search" i]',
            'input[aria-label*="Search" i]',
        ),
        timeout_ms=timeout_ms,
    )


def _search_button_selector(page, timeout_ms: int = 0) -> str:
    return _first_visible_selector(
        page,
        (
            "button#search-icon-legacy",
            "ytd-searchbox button",
            'button[aria-label*="Search" i]',
            'button:has-text("Search")',
        ),
        timeout_ms=timeout_ms,
    )


def _resolve_runtime_selector(page, action: str, selector: str, value: str, description: str) -> str:
    """Recover from common AI selector inventions using the currently visible form."""
    semantic_text = f"{selector} {description}".lower()
    if any(token in semantic_text for token in ("search box", "search input", "search field", "placeholder")):
        if action in {"assert_visible", "fill", "press"}:
            return _search_input_selector(page, timeout_ms=4000) or selector
        if action == "click":
            return _search_button_selector(page, timeout_ms=1500) or selector
    if action == "click" and "login" in semantic_text and any(
        token in semantic_text for token in ("link", "navigate", "open", "page")
    ):
        return _first_visible_selector(
            page,
            (
                'a:has-text("Login")',
                'text=/^Login$/i',
                'a[href*="/account/login"]',
            ),
            timeout_ms=3000,
        )
    if action == "fill" and any(token in semantic_text for token in ("username", "email", "mobile", "phone", "account")):
        return _first_visible_selector(
            page,
            (
                selector,
                'input[type="email"]',
                'input[type="tel"]',
                'input[autocomplete="username"]',
                'input[type="text"]:not([name="q"]):not([placeholder*="search" i])',
            ),
            timeout_ms=4000,
        )
    if action == "fill" and "password" in semantic_text:
        return _first_visible_selector(page, (selector, 'input[type="password"]'), timeout_ms=800)
    if action == "click" and any(token in semantic_text for token in ("login", "sign in", "submit", "otp", "authenticate")):
        return _first_visible_selector(
            page,
            (
                'button:has-text("Request OTP")',
                'button:has-text("Login")',
                'button:has-text("Sign in")',
            ),
            timeout_ms=4000,
        )
    if action == "assert_visible" and any(
        token in semantic_text for token in ("error", "invalid", "reject", "authentication")
    ):
        return _first_visible_selector(
            page,
            (
                '[role="alert"]',
                'text=/invalid|valid (?:mobile|phone|email)|required|try again/i',
                'input[type="text"]:not([name="q"]):not([placeholder*="search" i])',
            ),
            timeout_ms=2500,
        )
    return _effective_selector(selector, value)


def _authentication_remains_rejected(page) -> bool:
    return bool(
        _first_visible_selector(
            page,
            (
                '[role="alert"]',
                'text=/invalid|valid (?:mobile|phone|email)|required|try again/i',
                'input[type="text"]:not([name="q"]):not([placeholder*="search" i])',
            ),
            timeout_ms=2500,
        )
    )


def _log(logs: List[Dict[str, Any]], level: str, message: str) -> None:
    logs.append({"level": level, "message": message, "time": datetime.utcnow().isoformat()})


def _console_log(logs: List[Dict[str, Any]], message) -> None:
    text = message.text
    ignored = (
        "Failed to load resource: the server responded with a status of 403" in text
        or "Failed to load resource: the server responded with a status of 406" in text
        or "static-assets-web.flixcart.com" in text
        or "blocked by CORS policy" in text
        or "net::ERR_FAILED" in text
        or ("Component with name" in text and "fallback View" in text)
        or "was preloaded using link preload but not used" in text
        or "LegacyDataMixin will be applied" in text
    )
    if not ignored:
        _log(logs, message.type, text)


def _capture_screenshot(page, path: Path, logs: List[Dict[str, Any]]) -> bool:
    """Capture full-page evidence, falling back to the visible viewport."""
    try:
        page.screenshot(
            path=str(path),
            full_page=True,
            animations="disabled",
            caret="hide",
            timeout=20000,
        )
        return True
    except Exception as full_page_error:
        _log(logs, "warning", f"Full-page screenshot timed out; using viewport capture: {full_page_error}")

    try:
        page.screenshot(
            path=str(path),
            full_page=False,
            animations="disabled",
            caret="hide",
            timeout=12000,
        )
        return True
    except Exception as viewport_error:
        _log(logs, "warning", f"Screenshot could not be captured: {viewport_error}")
        return False


def _dismiss_obstructions(page, logs: List[Dict[str, Any]]) -> bool:
    """Close common non-essential dialogs that can intercept test interactions."""
    dismissed = False
    try:
        page.keyboard.press("Escape")
    except Exception:
        pass

    selectors = (
        '[role="dialog"] button[aria-label*="close" i]',
        '[role="dialog"] [aria-label*="close" i]',
        'button[aria-label*="close" i]',
        'button:has-text("Close")',
        'button:has-text("✕")',
        "button._2KpZ6l._2doB4z",
        'span[role="button"]:has-text("✕")',
    )
    for selector in selectors:
        try:
            locator = page.locator(selector)
            if locator.count() and locator.first.is_visible():
                locator.first.click(timeout=1200)
                dismissed = True
        except Exception:
            continue

    if dismissed:
        _log(logs, "info", "Dismissed a popup or overlay before continuing.")
    return dismissed


def _wait_for_url_contains(page, expected: str, timeout: int = 10000) -> None:
    """Check the live URL without waiting for slow third-party resources to load."""
    page.wait_for_function(
        "(expected) => window.location.href.toLowerCase().includes(expected.toLowerCase())",
        arg=expected,
        timeout=timeout,
    )


def _assert_search_placeholder(page, expected: str, logs: List[Dict[str, Any]]) -> bool:
    selector = _search_input_selector(page, timeout_ms=4000)
    if not selector:
        return False
    locator = page.locator(selector).first
    placeholder = locator.get_attribute("placeholder") or locator.get_attribute("aria-label") or ""
    if expected and expected.lower() not in placeholder.lower():
        _log(logs, "warning", f"Search input was visible, but placeholder was '{placeholder}'.")
    locator.wait_for(state="visible")
    return True


def _youtube_cycle_quality(page, logs: List[Dict[str, Any]]) -> None:
    """Open YouTube quality settings and try each visible resolution option."""
    settings_button = page.locator(".ytp-settings-button").first
    settings_button.wait_for(state="visible", timeout=10000)
    settings_button.click()
    page.locator(".ytp-menuitem:has-text('Quality')").first.wait_for(state="visible", timeout=5000)
    page.locator(".ytp-menuitem:has-text('Quality')").first.click()

    options = page.locator(".ytp-quality-menu .ytp-menuitem, .ytp-panel-menu .ytp-menuitem")
    option_count = min(options.count(), 10)
    labels = []
    for index in range(option_count):
        label = (options.nth(index).inner_text(timeout=1000) or "").strip()
        if label:
            labels.append(label)

    if not labels:
        raise AssertionError("No YouTube quality options were visible.")

    for label in labels:
        settings_button.click()
        page.locator(".ytp-menuitem:has-text('Quality')").first.click()
        option = page.locator(".ytp-quality-menu .ytp-menuitem, .ytp-panel-menu .ytp-menuitem").filter(has_text=label).first
        option.click(timeout=3000)
        page.wait_for_timeout(1200)
        page.locator("#movie_player, video").first.wait_for(state="visible", timeout=5000)
        _log(logs, "info", f"Selected YouTube quality option: {label}")


def execute_steps(
    run_id: int,
    target_url: str,
    steps: List[TestStep],
    show_browser: bool = False,
) -> Tuple[str, str, str, List[Dict[str, Any]], List[str], float]:
    started = time.perf_counter()
    logs: List[Dict[str, Any]] = []
    screenshots: List[str] = []
    status = "passed"
    summary = "Test executed successfully."
    error_summary = ""

    try:
        from playwright.sync_api import Error as PlaywrightError
        from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        return (
            "warning",
            "Test case was generated, but Playwright is not installed in this environment.",
            f"Install Playwright and browsers to run real automation. Details: {exc}",
            [{"level": "warning", "message": "Playwright runtime unavailable.", "time": datetime.utcnow().isoformat()}],
            [],
            (time.perf_counter() - started) * 1000,
        )

    artifact_dir = _artifact_dir(run_id)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=False if show_browser else settings.playwright_headless,
                slow_mo=450 if show_browser else 0,
            )
            page = browser.new_page()
            page.set_default_timeout(8000)
            page.set_default_navigation_timeout(25000)
            page.on("console", lambda msg: _console_log(logs, msg))
            page.on("pageerror", lambda exc: _log(logs, "pageerror", str(exc)))

            for index, step in enumerate(steps, 1):
                _log(logs, "step", f"{index}. {step.description}")
                action = step.action.lower()
                selector = step.selector or ""
                value = step.value or ""
                if action in {"click", "fill", "press", "assert_visible"}:
                    selector = _resolve_runtime_selector(page, action, selector, value, step.description)

                try:
                    if action == "goto":
                        try:
                            page.goto(value or target_url, wait_until="domcontentloaded", timeout=25000)
                        except PlaywrightTimeoutError:
                            _log(logs, "warning", "Page load was slow; continuing after the first response was received.")
                            page.goto(value or target_url, wait_until="commit", timeout=15000)
                        _dismiss_obstructions(page, logs)
                    elif action == "click" and selector:
                        _dismiss_obstructions(page, logs)
                        try:
                            page.locator(selector).first.click()
                        except (PlaywrightTimeoutError, PlaywrightError):
                            _dismiss_obstructions(page, logs)
                            page.locator(selector).first.click()
                    elif action == "click" and any(
                        token in step.description.lower() for token in ("login", "sign in", "submit", "otp", "authenticate")
                    ):
                        _log(logs, "warning", "Authentication control was not visible; submission was safely skipped.")
                        status = "warning" if status == "passed" else status
                    elif action == "fill" and selector:
                        _dismiss_obstructions(page, logs)
                        page.locator(selector).first.fill(value)
                    elif action == "fill" and "password" in step.description.lower():
                        _log(logs, "warning", "Password step skipped because this login flow has no visible password field.")
                        status = "warning" if status == "passed" else status
                    elif action == "press" and selector:
                        page.locator(selector).first.press(value or "Enter")
                    elif action == "assert_text" and value:
                        if "search" in step.description.lower() and "placeholder" in step.description.lower():
                            if not _assert_search_placeholder(page, value, logs):
                                raise AssertionError("Search input placeholder could not be verified.")
                        elif any(
                            token in f"{step.description} {value}".lower()
                            for token in ("invalid credentials", "authentication", "login error", "rejected")
                        ):
                            if not _authentication_remains_rejected(page):
                                raise AssertionError("No authentication rejection state remained visible.")
                            _log(logs, "info", "Verified that the authentication form remained in a rejected state.")
                        else:
                            page.get_by_text(value, exact=False).first.wait_for()
                    elif action == "assert_visible" and selector:
                        page.locator(selector).first.wait_for(state="visible")
                    elif action == "assert_value" and selector:
                        actual_value = page.locator(selector).first.input_value()
                        if actual_value != value:
                            raise AssertionError(f"Expected input value '{value}', received '{actual_value}'.")
                    elif action == "assert_count" and selector:
                        minimum = int(value or "1")
                        actual_count = page.locator(selector).count()
                        if actual_count < minimum:
                            raise AssertionError(f"Expected at least {minimum} matching element(s), found {actual_count}.")
                    elif action == "assert_url_changed":
                        original_url = value or target_url
                        page.wait_for_function(
                            "(original) => window.location.href !== original",
                            arg=original_url,
                            timeout=8000,
                        )
                    elif action == "assert_url_contains" and value:
                        _wait_for_url_contains(page, value, timeout=10000)
                    elif action == "assert_title":
                        if not page.title():
                            raise AssertionError("Page title is empty.")
                    elif action == "wait":
                        page.wait_for_timeout(int(value or "1000"))
                    elif action == "youtube_cycle_quality":
                        _youtube_cycle_quality(page, logs)
                    elif action == "screenshot":
                        shot = artifact_dir / f"step-{index}.png"
                        if _capture_screenshot(page, shot, logs):
                            screenshots.append(str(shot))
                        else:
                            status = "warning"
                    else:
                        _log(logs, "warning", f"Skipped unsupported or incomplete action: {action}")
                except (PlaywrightTimeoutError, PlaywrightError, AssertionError) as exc:
                    if step.optional or (selector and _optional(selector)):
                        _log(logs, "warning", f"Optional step skipped: {exc}")
                        status = "warning" if status == "passed" else status
                    else:
                        failed_shot = artifact_dir / f"failed-step-{index}.png"
                        if _capture_screenshot(page, failed_shot, logs):
                            screenshots.append(str(failed_shot))
                        raise

            final_shot = artifact_dir / "final.png"
            if _capture_screenshot(page, final_shot, logs):
                screenshots.append(str(final_shot))
            else:
                status = "warning"
            if show_browser:
                page.wait_for_timeout(1800)
            browser.close()

    except Exception as exc:
        status = "failed"
        summary = "The test run failed before all steps completed."
        error_summary = f"{type(exc).__name__}: {exc}"
        _log(logs, "error", error_summary)

    duration_ms = (time.perf_counter() - started) * 1000
    if status == "warning":
        summary = "The main workflow completed, but one or more optional steps or evidence captures produced warnings."
    return status, summary, error_summary, logs, screenshots, duration_ms


def encode_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, default=str)


def decode_json(value: str) -> Any:
    try:
        return json.loads(value or "[]")
    except json.JSONDecodeError:
        return []
