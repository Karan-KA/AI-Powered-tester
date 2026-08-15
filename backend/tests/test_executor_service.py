from pathlib import Path

from app.services.executor_service import (
    _assert_search_placeholder,
    _capture_screenshot,
    _console_log,
    _dismiss_obstructions,
    _effective_selector,
    _resolve_runtime_selector,
    _youtube_cycle_quality,
    _wait_for_url_contains,
)


class FakeConsoleMessage:
    def __init__(self, text, message_type="error"):
        self.text = text
        self.type = message_type


class ScreenshotFallbackPage:
    def __init__(self):
        self.calls = []

    def screenshot(self, **kwargs):
        self.calls.append(kwargs)
        if kwargs["full_page"]:
            raise TimeoutError("full page timed out")


class ScreenshotFailurePage:
    def screenshot(self, **kwargs):
        raise TimeoutError("capture timed out")


class FakeKeyboard:
    def __init__(self):
        self.keys = []

    def press(self, key):
        self.keys.append(key)


class FakeLocator:
    def __init__(self, visible=False):
        self.visible = visible
        self.first = self
        self.clicked = False

    def count(self):
        return int(self.visible)

    def is_visible(self):
        return self.visible

    def click(self, **kwargs):
        self.clicked = True

    def nth(self, index):
        return self

    def wait_for(self, **kwargs):
        return None

    def get_attribute(self, name):
        if name == "placeholder":
            return "Search"
        return None


class PopupPage:
    def __init__(self):
        self.keyboard = FakeKeyboard()
        self.close = FakeLocator(visible=True)

    def locator(self, selector):
        if selector == '[role="dialog"] button[aria-label*="close" i]':
            return self.close
        return FakeLocator()


class LoginPage:
    def locator(self, selector):
        visible = selector in {
            'a:has-text("Login")',
            'input[type="text"]:not([name="q"]):not([placeholder*="search" i])',
            'button:has-text("Request OTP")',
        }
        return FakeLocator(visible=visible)


class YouTubeLikePage:
    def locator(self, selector):
        visible = selector == 'input[name="search_query"]'
        return FakeLocator(visible=visible)


class UrlPage:
    def __init__(self):
        self.call = None

    def wait_for_function(self, expression, **kwargs):
        self.call = (expression, kwargs)


class QualityOption:
    def __init__(self, label):
        self.label = label
        self.clicked = False

    def inner_text(self, **kwargs):
        return self.label

    def click(self, **kwargs):
        self.clicked = True

    def wait_for(self, **kwargs):
        return None


class QualityLocator:
    def __init__(self, options=None):
        self.options = options or []
        self.first = self.options[0] if self.options else QualityOption("")

    def count(self):
        return len(self.options)

    def nth(self, index):
        return self.options[index]

    def filter(self, has_text):
        return QualityLocator([option for option in self.options if option.label == has_text])


class YouTubeQualityPage:
    def __init__(self):
        self.options = [QualityOption("720p"), QualityOption("480p")]
        self.waits = []

    def locator(self, selector):
        if selector == ".ytp-settings-button":
            return QualityLocator([QualityOption("settings")])
        if selector == ".ytp-menuitem:has-text('Quality')":
            return QualityLocator([QualityOption("Quality")])
        if selector == ".ytp-quality-menu .ytp-menuitem, .ytp-panel-menu .ytp-menuitem":
            return QualityLocator(self.options)
        if selector == "#movie_player, video":
            return QualityLocator([QualityOption("player")])
        return QualityLocator([])

    def wait_for_timeout(self, value):
        self.waits.append(value)


def test_screenshot_falls_back_to_viewport(tmp_path):
    logs = []
    page = ScreenshotFallbackPage()

    assert _capture_screenshot(page, Path(tmp_path) / "shot.png", logs) is True
    assert [call["full_page"] for call in page.calls] == [True, False]
    assert logs[0]["level"] == "warning"


def test_screenshot_failure_returns_false(tmp_path):
    logs = []

    assert _capture_screenshot(ScreenshotFailurePage(), Path(tmp_path) / "shot.png", logs) is False
    assert len(logs) == 2


def test_known_youtube_resource_noise_is_filtered():
    logs = []
    _console_log(
        logs,
        FakeConsoleMessage("Failed to load resource: the server responded with a status of 403 ()"),
    )
    _console_log(logs, FakeConsoleMessage("Real application error"))

    assert len(logs) == 1
    assert logs[0]["message"] == "Real application error"


def test_known_flipkart_resource_noise_is_filtered():
    logs = []
    _console_log(
        logs,
        FakeConsoleMessage(
            "Access to fetch at 'https://static-assets-web.flixcart.com/file.svg' "
            "has been blocked by CORS policy"
        ),
    )
    _console_log(logs, FakeConsoleMessage("Failed to load resource: the server responded with a status of 406 ()"))

    assert logs == []


def test_popup_dismissal_uses_escape_and_visible_close_control():
    logs = []
    page = PopupPage()

    assert _dismiss_obstructions(page, logs) is True
    assert page.keyboard.keys == ["Escape"]
    assert page.close.clicked is True
    assert logs[0]["level"] == "info"


def test_url_contains_does_not_wait_for_page_load():
    page = UrlPage()

    _wait_for_url_contains(page, "https://www.flipkart.com/viewcart")

    assert page.call[1]["arg"] == "https://www.flipkart.com/viewcart"
    assert page.call[1]["timeout"] == 10000


def test_generic_link_selector_is_narrowed_by_visible_label():
    assert _effective_selector("a", "Cart") == "text=/^Cart$/i"
    assert _effective_selector("a.product", "Cart") == "a.product"


def test_runtime_recovers_invented_flipkart_login_selectors():
    page = LoginPage()

    login_link = _resolve_runtime_selector(
        page,
        "click",
        "a",
        "",
        "Click the Login link to navigate to login page",
    )
    account = _resolve_runtime_selector(
        page,
        "fill",
        'input[name="username"]',
        "invalid",
        "Enter invalid username",
    )
    submit = _resolve_runtime_selector(
        page,
        "click",
        'button[type="submit"]',
        "",
        "Submit login form",
    )

    assert login_link == 'a:has-text("Login")'
    assert account == 'input[type="text"]:not([name="q"]):not([placeholder*="search" i])'
    assert submit == 'button:has-text("Request OTP")'


def test_search_placeholder_uses_visible_input_not_hidden_text():
    logs = []

    assert _assert_search_placeholder(YouTubeLikePage(), "Search", logs) is True
    assert logs == []


def test_youtube_quality_cycles_visible_options():
    logs = []
    page = YouTubeQualityPage()

    _youtube_cycle_quality(page, logs)

    assert all(option.clicked for option in page.options)
    assert [log["message"] for log in logs] == [
        "Selected YouTube quality option: 720p",
        "Selected YouTube quality option: 480p",
    ]
