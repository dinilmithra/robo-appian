"""Library-owned browser event collection and recorder lifecycle."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from .model import Recording, digest, issues, safe_url


class AppianRecorder:
    """Attach a paused recorder to a dedicated, non-persistent browser context.

    Raw browser instrumentation is intentionally confined to robo-appian.
    Consumers use this service rather than Playwright event/DOM APIs.
    """
    def __init__(self, output: str | Path, *, name: str = "Recorded workflow", recording: Recording | None = None):
        self.output = Path(output)
        self.recording = recording or Recording(name)
        self.running = False
        self.verifying = False
        self.finished = False
        self._primary = None
        self._pages: list[Any] = []
        self._inspection: list[dict] = []

    @property
    def recording_path(self) -> Path:
        return self.output / "recording.json"

    def state(self) -> dict:
        steps = []
        for step in self.recording.data["steps"]:
            steps.append({**step, "approved": step.get("approval") == self.recording.approval_digest(step), "problems": issues(step)})
        return {"recording": self.running, "verifying": self.verifying,
                "steps": steps, "issues": self.recording.export_issues(),
                "inspection": self._inspection}

    def save(self) -> Path:
        self.recording.save(self.recording_path)
        return self.recording_path

    def _bridge(self, source: dict, message: dict) -> dict:
        if not isinstance(message, dict) or len(json.dumps(message)) > 250_000:
            raise ValueError("Invalid or oversized recorder message.")
        page = source["page"]
        if page not in self._pages:
            self._pages.append(page)
        command = message.get("command")
        if command == "toggle":
            if page is not self._primary:
                raise ValueError("Start recording from the original browser page.")
            self.running = not self.running; self.verifying = False
            if self.running and not self.recording.data["start_url"]:
                self.recording.data["start_url"] = safe_url(page.url)
        elif command == "verify":
            if not self.running:
                raise ValueError("Start recording before adding a verification.")
            self.verifying = not self.verifying
        elif command == "verify_off":
            self.verifying = False
        elif command == "event" and self.running:
            payload = message.get("payload")
            if not isinstance(payload, dict) or not isinstance(payload.get("target"), dict):
                raise ValueError("A semantic target is required.")
            payload = dict(payload)
            payload["page"] = f"page{self._pages.index(page) + 1}"
            if source.get("frame") is not page.main_frame:
                payload["blocker"] = "Iframe interaction needs a frame-aware Appian adapter; v1 exports main-frame tests only."
            self.recording.add(payload)
            self.save()
        elif command == "review":
            self.recording.review(str(message.get("id")), approve=bool(message.get("approve")), value=str(message.get("value", "")))
            self.save()
        elif command == "remove":
            self.recording.data["steps"] = [s for s in self.recording.data["steps"] if s["id"] != message.get("id")]
            self.save()
        elif command == "inspect":
            inventory = message.get("inspection", [])
            if not isinstance(inventory, list):
                raise ValueError("Inventory must be a list.")
            self._inspection = inventory[:500]
            self.recording.data["pages"].append({"url": safe_url(page.url), "components": self._inspection})
            self.save()
        elif command in {"save", "finish"}:
            self.save()
            if command == "finish":
                self.running = False; self.finished = True
        return self.state()

    def attach(self, context: Any, primary_page: Any) -> None:
        """Register bindings/init scripts once before navigating the fresh browser."""
        self._primary = primary_page; self._pages = [primary_page]
        script = Path(__file__).with_name("recorder.js").read_text(encoding="utf-8")
        context.expose_binding("__roboRecorderBridge", self._bridge)
        context.add_init_script(script=script)
        # Also support attaching to an already-created page in this owned context.
        primary_page.evaluate(script)
        context.on("page", self._on_page)

    def _on_page(self, page: Any) -> None:
        if page not in self._pages:
            self._pages.append(page)
        if self.running:
            self.recording.add({"page": f"page{self._pages.index(page) + 1}",
                                "action": "unsupported", "target": {"component": "unsupported"},
                                "blocker": "A popup opened. Multi-page playback requires a page-switch adapter."})
            self.save()

    def inspect_page(self, page: Any) -> list[dict]:
        """Inspect a page attached to this recording context without performing actions."""
        return page.evaluate("() => window.__roboRecorderInspect()")


def record_browser(url: str, output: str | Path, *, name: str = "Recorded workflow", channel: str | None = None, recording: Recording | None = None) -> Path:
    """Open a fresh visible Chromium browser, record/review, and save on completion.

    No cookies, profile, authentication storage or existing personal tabs are reused.
    The short loop wait only services recorder UI events; it is never emitted into tests.
    """
    if urlsplit(url).scheme not in {"http", "https", "file", "about"}:
        raise ValueError("Use an http(s) URL or the included local demo.")
    recorder = AppianRecorder(output, name=name, recording=recording)
    if recorder.recording_path.exists() and recording is None:
        raise FileExistsError("Recording already exists. Choose a new output directory or use review.")
    from playwright.sync_api import Error, sync_playwright

    with sync_playwright() as driver:
        browser = driver.chromium.launch(headless=False, **({"channel": channel} if channel else {}))
        try:
            context = browser.new_context()
            try:
                page = context.new_page()
                recorder.attach(context, page)
                page.goto(url)
                print("Recorder paused. Sign in manually, then click Start recording on a stable entry page.")
                try:
                    while not recorder.finished and context.pages:
                        context.pages[0].wait_for_timeout(100)
                except KeyboardInterrupt:
                    print("Recording interrupted; draft saved.")
                except Error:
                    if browser.is_connected() and context.pages:
                        raise
                finally:
                    recorder.save()
            finally:
                context.close()
        finally:
            browser.close()
    return recorder.recording_path
