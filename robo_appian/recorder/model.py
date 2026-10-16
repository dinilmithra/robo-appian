"""Versioned, reviewable semantic recordings. No browser dependency."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

SCHEMA_VERSION = 1
COMPONENTS = {"textbox", "date", "dropdown", "checkbox", "radio", "button", "link", "tab", "menu", "text", "grid_cell", "unsupported"}
ACTIONS = {"fill", "select", "check", "uncheck", "click", "open", "assert_visible", "assert_value", "assert_text", "unsupported"}
SECRET = re.compile(r"password|passwd|user.?name|secret|token|authorization|credential|social.security|ssn", re.I)


def safe_url(value: str) -> str:
    """Keep routing, excluding credentials, arbitrary query data and fragments."""
    url = urlsplit(value)
    host = url.hostname or ""
    if url.port:
        host += f":{url.port}"
    query = urlencode([(k, v) for k, v in parse_qsl(url.query) if k == "page"])
    return urlunsplit((url.scheme, host, url.path, query, ""))


def digest(step: dict) -> str:
    content = {k: v for k, v in step.items() if k not in {"approval", "id"}}
    return hashlib.sha256(json.dumps(content, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def issues(step: dict) -> list[str]:
    """Reject unrepresentable targets instead of producing selector fallbacks."""
    target = step.get("target", {})
    kind, action = target.get("component"), step.get("action")
    result = []
    if kind not in COMPONENTS or kind == "unsupported" or action not in ACTIONS or action == "unsupported":
        result.append("Unsupported component or action; map or remove this step.")
    if step.get("blocker"):
        result.append(str(step["blocker"]))
    if step.get("page", "page1") != "page1":
        result.append("Popup pages require a page-switch adapter; not supported in v1.")
    if target.get("native_select"):
        result.append("Native selects require a generic web adapter.")
    if target.get("ambiguous"):
        result.append("The semantic target is ambiguous; refine its mapping.")
    if target.get("dialog") and kind != "button":
        result.append("Only dialog buttons have a verified scoped factory in v1.")
    if kind == "grid_cell":
        grid = target.get("grid", {})
        if not grid.get("header") or not isinstance(grid.get("row_number"), int) or grid["row_number"] < 1 or not grid.get("column_name"):
            result.append("Grid cells require header, one-based row and named column.")
        if action != "assert_text":
            result.append("Grid v1 records cell text assertions; editable cells require mapping.")
    elif kind == "menu":
        if not target.get("path") or not all(isinstance(x, str) and x.strip() for x in target["path"]):
            result.append("A named menu path is required.")
    elif kind in {"button", "link", "tab", "text"}:
        if not target.get("name"):
            result.append("A visible semantic name is required.")
    elif kind in {"textbox", "date", "dropdown", "checkbox", "radio"}:
        if not target.get("label") and not (kind in {"textbox", "date"} and target.get("placeholder")):
            result.append("A field label or supported placeholder is required.")
    legal = {
        "textbox": {"fill", "select", "assert_value"}, "date": {"fill", "assert_value"},
        "dropdown": {"select", "assert_value"}, "checkbox": {"check", "uncheck"},
        "radio": {"select"}, "button": {"click", "assert_visible"},
        "link": {"click", "assert_visible"}, "tab": {"select"},
        "menu": {"open", "click"}, "text": {"assert_visible"},
        "grid_cell": {"assert_text"},
    }
    if kind in legal and action not in legal[kind]:
        result.append("Action is not supported by this component's public API.")
    if action == "assert_visible" and kind == "text" and target.get("dialog"):
        result.append("Scoped dialog text is not supported in v1.")
    if action in {"fill", "select", "assert_value", "assert_text"} and not isinstance(step.get("value"), str):
        result.append("This action requires a string value.")
    if action == "select" and kind == "textbox" and not isinstance(step.get("search_text"), str):
        result.append("A searchable textbox selection requires search_text.")
    return list(dict.fromkeys(result))


class Recording:
    """Hold normalized actions and content-bound human approvals."""
    def __init__(self, name: str = "Recorded workflow"):
        self.data = {"schema_version": SCHEMA_VERSION, "name": name,
                     "created_at": datetime.now(timezone.utc).isoformat(),
                     "start_url": "", "steps": [], "pages": [],
                     "notes": ["Observed values are proposed expectations until explicitly approved."]}

    @classmethod
    def load(cls, path: str | Path) -> Recording:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if data.get("schema_version") != SCHEMA_VERSION:
            raise ValueError("Unsupported recording schema version.")
        if not isinstance(data.get("steps"), list):
            raise ValueError("Recording steps must be a list.")
        if not all(isinstance(s, dict) and isinstance(s.get("target"), dict) and
                   isinstance(s.get("id"), str) and re.fullmatch(r"step-[0-9]+", s["id"])
                   for s in data["steps"]):
            raise ValueError("Invalid step structure.")
        if len({s["id"] for s in data["steps"]}) != len(data["steps"]):
            raise ValueError("Step IDs must be unique.")
        obj = cls(); obj.data = data
        return obj

    def add(self, payload: dict) -> dict | None:
        target = dict(payload.get("target", {}))
        # Defence in depth: do not retain values from credential controls.
        if payload.get("sensitive") or SECRET.search(" ".join(str(target.get(k, "")) for k in ("label", "name", "placeholder"))):
            return None
        step = {"id": "", "page": str(payload.get("page", "page1")),
                "action": str(payload.get("action", "unsupported")), "target": target,
                "value": payload.get("value", ""), "approval": None}
        for key in ("search_text", "blocker"):
            if key in payload:
                step[key] = str(payload[key])
        steps = self.data["steps"]
        # Collapse blur/change duplicates and lookup typing into a logical select.
        if steps and steps[-1]["target"] == target and steps[-1]["page"] == step["page"]:
            previous = steps[-1]
            if previous["action"] == "fill" and step["action"] in {"fill", "select"}:
                step["id"] = previous["id"]; steps[-1] = step
                return step
            if previous["action"] == step["action"] and previous.get("value") == step.get("value"):
                return previous
        if steps and target.get("component") == "menu" and step["action"] == "click":
            previous = steps[-1]
            if previous["action"] == "open" and previous["target"].get("component") == "menu" and target.get("path", [])[:1] == previous["target"].get("path"):
                steps.pop()
        step["id"] = "step-" + str(max([int(s["id"].split("-")[-1]) for s in steps] + [0]) + 1)
        steps.append(step)
        return step

    def approval_digest(self, step: dict) -> str:
        """Bind approval to both step content and the recording entry URL."""
        return digest({**step, "recording_start_url": self.data.get("start_url", "")})

    def review(self, step_id: str, *, approve: bool, value: str | None = None) -> None:
        step = next(s for s in self.data["steps"] if s["id"] == step_id)
        if value is not None:
            step["value"] = value
        step["approval"] = None
        if approve:
            problems = issues(step)
            if problems:
                raise ValueError("; ".join(problems))
            step["approval"] = self.approval_digest(step)

    def export_issues(self) -> list[str]:
        steps = self.data["steps"]; result = []
        if not steps:
            result.append("Record at least one action.")
        if not any(s.get("action", "").startswith("assert_") for s in steps):
            result.append("Add and approve at least one explicit verification.")
        if not self.data.get("start_url"):
            result.append("A start URL is required.")
        elif urlsplit(self.data["start_url"]).scheme not in {"http", "https", "file"}:
            result.append("The recording needs an http(s) or local demo entry URL.")
        for step in steps:
            result.extend(f"{step['id']}: {msg}" for msg in issues(step))
            if step.get("approval") != self.approval_digest(step):
                result.append(f"{step['id']}: review and approve this exact step content.")
        return result

    def save(self, path: str | Path) -> None:
        path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_text(json.dumps(self.data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        tmp.replace(path)
