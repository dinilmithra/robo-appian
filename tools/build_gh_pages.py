from __future__ import annotations

import ast
import html
import re
import shutil
from pathlib import Path

import mistune

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SITE = ROOT / "site"
PKG = ROOT / "robo_appian"

SITE_NAME = "robo-appian"
SITE_DESCRIPTION = "Reusable Playwright components for Appian UI automation"

NAV = [
    ("Home", "index.html"),
    ("Getting Started", "getting-started/installation/index.html"),
    ("Components", "guides/components/index.html"),
    ("Guides", "guides/development/index.html"),
    ("API Reference", "api/index.html"),
]

API_MAP = {
    "button": ("Button", PKG / "components" / "Button.py"),
    "checkbox": ("CheckBox", PKG / "components" / "CheckBox.py"),
    "dropdown": ("Dropdown", PKG / "components" / "Dropdown.py"),
    "input-date": ("InputDate", PKG / "components" / "InputDate.py"),
    "input-text": ("InputText", PKG / "components" / "InputText.py"),
    "link": ("Link", PKG / "components" / "Link.py"),
    "menu-button": ("MenuButton", PKG / "components" / "MenuButton.py"),
    "radio-select": ("RadioSelect", PKG / "components" / "RadioSelect.py"),
    "record-list": ("RecordList", PKG / "components" / "RecordList.py"),
    "region": ("Region", PKG / "components" / "Region.py"),
    "search-dropdown": ("SearchDropdown", PKG / "components" / "SearchDropdown.py"),
    "search-input": ("SearchInput", PKG / "components" / "SearchInput.py"),
    "tab": ("Tab", PKG / "components" / "Tab.py"),
    "table": ("Table", PKG / "components" / "Table.py"),
    "text": ("Text", PKG / "components" / "Text.py"),
    "component-utils": ("ComponentUtils", PKG / "utils" / "ComponentUtils.py"),
    "scope": ("Scope helpers", PKG / "utils" / "types.py"),
}

markdown = mistune.create_markdown(plugins=["strikethrough", "table", "task_lists", "url"])


def rel_prefix(path: str) -> str:
    depth = len(Path(path).parts) - 1
    return "../" * depth


def nav_html(current: str, prefix: str) -> str:
    links = []
    for label, target in NAV:
        active = " active" if current == label else ""
        links.append(f'<a class="nav-link{active}" href="{prefix}{target}">{html.escape(label)}</a>')
    return "".join(links)


def page_shell(title: str, body: str, path: str, current: str, description: str | None = None) -> str:
    prefix = rel_prefix(path)
    desc = description or SITE_DESCRIPTION
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{html.escape(desc)}">
  <meta name="color-scheme" content="light dark">
  <title>{html.escape(title)} · {SITE_NAME}</title>
  <link rel="stylesheet" href="{prefix}assets/styles.css">
  <script defer src="{prefix}assets/site.js"></script>
</head>
<body data-page="{html.escape(current)}">
  <header class="site-header">
    <div class="header-inner">
      <a class="brand" href="{prefix}index.html" aria-label="robo-appian home">
        <span class="brand-mark" aria-hidden="true">◆</span>
        <span>robo-appian</span>
      </a>
      <nav class="top-nav" aria-label="Primary navigation">{nav_html(current, prefix)}</nav>
      <div class="header-actions">
        <button class="search-button" type="button" data-search-toggle aria-label="Search documentation">⌕ <span>Search</span></button>
        <button class="theme-button" type="button" data-theme-toggle aria-label="Toggle color theme">◐</button>
      </div>
    </div>
  </header>
  <div class="search-panel" data-search-panel hidden>
    <div class="search-panel-inner">
      <input type="search" placeholder="Search robo-appian docs" aria-label="Search documentation" data-search-input>
      <div class="search-results" data-search-results></div>
    </div>
  </div>
  <main>{body}</main>
  <footer class="site-footer">
    <div><strong>robo-appian</strong> · Reusable Playwright helpers for Appian UI automation.</div>
    <div class="footer-links"><a href="{prefix}getting-started/installation/index.html">Install</a><a href="{prefix}guides/components/index.html">Components</a><a href="{prefix}api/index.html">API</a></div>
  </footer>
</body>
</html>'''


def write_page(path: str, title: str, body: str, current: str, description: str | None = None) -> None:
    target = SITE / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(page_shell(title, body, path, current, description), encoding="utf-8")


def clean_markdown(text: str) -> str:
    # Convert Material button syntax to ordinary links and simplify admonitions.
    text = re.sub(r'\]\(([^)]+)\.md\)\{[^}]+\}', r'](\1/index.html)', text)
    text = re.sub(r'\]\(([^)]+)\.md\)', r'](\1/index.html)', text)
    text = text.replace('<div class="grid cards" markdown>', '').replace('</div>', '')
    text = text.replace('<div class="component-chips" markdown>', '')
    text = re.sub(r'^!!!\s+(\w+)\s+"([^"]+)"\s*$', r'### \2', text, flags=re.M)
    text = re.sub(r'^\s{4}(`?[^\n]+)$', r'\1', text, flags=re.M)
    # Remove mkdocstrings directives; API pages are generated from source separately.
    text = re.sub(r'^:::\s+[^\n]+(?:\n(?:\s{4,}.*|\s*)*)?', '', text, flags=re.M)
    return text


def markdown_body(source: Path, eyebrow: str | None = None) -> str:
    text = clean_markdown(source.read_text(encoding="utf-8"))
    rendered = markdown(text)
    eyebrow_html = f'<div class="eyebrow">{html.escape(eyebrow)}</div>' if eyebrow else ''
    return f'<section class="content-wrap"><article class="docs-article">{eyebrow_html}{rendered}</article></section>'


def home_body() -> str:
    components = [v[0] for k, v in API_MAP.items() if k != "scope"]
    chips = ''.join(f'<a class="chip" href="api/{slug}/index.html">{html.escape(name)}</a>' for slug, (name, _) in API_MAP.items())
    return f'''
<section class="hero">
  <div class="hero-grid">
    <div class="hero-copy">
      <div class="hero-badges"><span>Python</span><span>Playwright</span><span>Appian</span></div>
      <h1>Automate Appian UI interactions<br><span>with less boilerplate</span></h1>
      <p class="hero-lede"><code>robo-appian</code> is a focused Python library of reusable Playwright helpers for common Appian controls. Keep low-level interaction mechanics in one place while your test project stays focused on workflows, business rules, assertions, and test data.</p>
      <div class="hero-actions">
        <a class="button primary" href="getting-started/installation/index.html">Get Started →</a>
        <a class="button" href="getting-started/quick-start/index.html">Quick Start</a>
        <a class="button" href="api/index.html">Browse API</a>
      </div>
      <div class="install-line"><span>$</span><code>pip install robo-appian</code><button type="button" data-copy="pip install robo-appian">Copy</button></div>
    </div>
    <div class="hero-visual" aria-label="robo-appian architecture illustration">
      <div class="browser-card">
        <div class="browser-top"><span></span><span></span><span></span></div>
        <div class="appian-label">Appian</div>
        <div class="skeleton"><i></i><i></i><i></i><i></i></div>
      </div>
      <div class="flow-card tests"><strong>Tests</strong><span>Workflows</span><span>Business Logic</span><span>Test Data</span></div>
      <div class="flow-arrow one">→</div>
      <div class="flow-card library"><div class="robot">◉</div><strong>robo-appian</strong><span>Playwright Helpers</span></div>
      <div class="flow-arrow two">→</div>
      <div class="flow-card playwright"><strong>Playwright</strong><span>Browser automation</span></div>
    </div>
  </div>
</section>

<section class="section-shell split-section">
  <div>
    <div class="section-kicker">Why robo-appian?</div>
    <h2>Keep tests readable and interaction behavior consistent</h2>
    <div class="feature-grid">
      <div class="feature-card"><span>◎</span><div><strong>Focus on business logic</strong><p>Keep application workflows, rules, and assertions in the consumer project.</p></div></div>
      <div class="feature-card"><span>✣</span><div><strong>Consistent interaction patterns</strong><p>Standardize Appian control behavior across multiple flows and suites.</p></div></div>
      <div class="feature-card"><span>◷</span><div><strong>Reduced maintenance</strong><p>Fix generic UI mechanics once instead of repeating the same locator changes.</p></div></div>
      <div class="feature-card"><span>◌</span><div><strong>Fits your framework</strong><p>Use the helpers selectively alongside your own fixtures and direct Playwright code.</p></div></div>
    </div>
  </div>
  <div class="code-panel">
    <div class="code-panel-title"><span>Quick example</span><button type="button" data-copy-target="home-code">Copy</button></div>
    <pre id="home-code"><code>from robo_appian import Button, Dropdown, InputText


def create_request(page):
    InputText.fill_by_label(page, "Request Name", "Example Request")
    Dropdown.select(page, "Request Type", "Travel")
    Button.click(page, "Submit")</code></pre>
  </div>
</section>

<section class="section-shell">
  <div class="section-kicker">Supported components</div>
  <h2>A focused API for common Appian controls</h2>
  <div class="chips">{chips}</div>
</section>

<section class="section-shell architecture">
  <div class="section-kicker">Architecture</div>
  <h2>Clear separation between reusable mechanics and application behavior</h2>
  <p class="section-copy"><code>robo-appian</code> provides generic component helpers. Application-specific workflow rules, labels, waits, data, and business logic stay in your test project.</p>
  <div class="architecture-flow">
    <div><strong>Tests</strong><span>Scenarios & assertions</span></div><b>→</b>
    <div><strong>Application Flow</strong><span>Business logic</span></div><b>→</b>
    <div class="highlight"><strong>robo-appian</strong><span>Component helpers</span></div><b>→</b>
    <div><strong>Playwright</strong><span>Browser engine</span></div>
  </div>
</section>

<section class="section-shell start-section">
  <div class="section-kicker">Start building</div>
  <h2>Everything you need to get productive</h2>
  <div class="next-grid">
    <a href="getting-started/installation/index.html"><span>↗</span><div><strong>Installation</strong><small>Install robo-appian and configure Playwright.</small></div><b>→</b></a>
    <a href="getting-started/quick-start/index.html"><span>▣</span><div><strong>Quick Start</strong><small>Build a first component-driven automation flow.</small></div><b>→</b></a>
    <a href="api/index.html"><span>▤</span><div><strong>API Reference</strong><small>Browse classes, signatures, and source-backed docs.</small></div><b>→</b></a>
  </div>
</section>'''


def annotation_text(node: ast.expr | None) -> str:
    if node is None:
        return ""
    try:
        return ast.unparse(node)
    except Exception:
        return ""


def signature_for(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    args = fn.args
    parts: list[str] = []
    pos = list(args.posonlyargs) + list(args.args)
    defaults = [None] * (len(pos) - len(args.defaults)) + list(args.defaults)
    for arg, default in zip(pos, defaults):
        if arg.arg in {"self", "cls"}:
            continue
        text = arg.arg
        ann = annotation_text(arg.annotation)
        if ann:
            text += f": {ann}"
        if default is not None:
            try:
                text += f" = {ast.unparse(default)}"
            except Exception:
                text += " = ..."
        parts.append(text)
    if args.vararg:
        parts.append("*" + args.vararg.arg)
    elif args.kwonlyargs:
        parts.append("*")
    for arg, default in zip(args.kwonlyargs, args.kw_defaults):
        text = arg.arg
        ann = annotation_text(arg.annotation)
        if ann:
            text += f": {ann}"
        if default is not None:
            try:
                text += f" = {ast.unparse(default)}"
            except Exception:
                text += " = ..."
        parts.append(text)
    if args.kwarg:
        parts.append("**" + args.kwarg.arg)
    ret = annotation_text(fn.returns)
    return f"{fn.name}({', '.join(parts)})" + (f" -> {ret}" if ret else "")


def doc_to_html(doc: str | None) -> str:
    if not doc:
        return '<p class="muted">No public docstring provided.</p>'
    # Google-style headings become readable subsections.
    text = html.escape(doc.strip())
    lines = text.splitlines()
    out: list[str] = []
    in_list = False
    for line in lines:
        raw = line.strip()
        if raw in {"Args:", "Returns:", "Raises:", "Examples:", "Example:", "Notes:", "Note:"}:
            if in_list:
                out.append("</ul>"); in_list = False
            out.append(f"<h4>{raw[:-1]}</h4>")
        elif re.match(r'^[A-Za-z_][\w]*(?:\s*\([^)]*\))?:\s+', raw):
            if not in_list:
                out.append('<ul class="api-detail-list">'); in_list = True
            name, desc = raw.split(":", 1)
            out.append(f"<li><code>{name}</code><span>{desc.strip()}</span></li>")
        elif raw:
            if in_list:
                out.append("</ul>"); in_list = False
            out.append(f"<p>{raw}</p>")
    if in_list:
        out.append("</ul>")
    return "".join(out)


def api_class_page(slug: str, display: str, source: Path) -> str:
    tree = ast.parse(source.read_text(encoding="utf-8"))
    class_node = next((n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == display), None)
    if class_node is None:
        # types.py / Scope helper fallback: list public functions/classes.
        members = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and not n.name.startswith("_")]
        cards = []
        for n in members:
            if isinstance(n, ast.ClassDef):
                cards.append(f'<section class="api-member"><h3><code>class {html.escape(n.name)}</code></h3>{doc_to_html(ast.get_docstring(n))}</section>')
            else:
                cards.append(f'<section class="api-member"><h3><code>{html.escape(signature_for(n))}</code></h3>{doc_to_html(ast.get_docstring(n))}</section>')
        return f'<section class="content-wrap"><article class="docs-article api-page"><div class="eyebrow">API Reference</div><h1>{html.escape(display)}</h1><p>Public helpers from <code>{html.escape(source.relative_to(ROOT).as_posix())}</code>.</p>{"".join(cards)}</article></section>'

    class_doc = doc_to_html(ast.get_docstring(class_node))
    method_cards = []
    for node in class_node.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) or node.name.startswith("_"):
            continue
        decorators = [annotation_text(d) for d in node.decorator_list]
        badge = ""
        if "staticmethod" in decorators:
            badge = '<span class="api-badge">static</span>'
        elif "classmethod" in decorators:
            badge = '<span class="api-badge">class</span>'
        method_cards.append(
            f'<section class="api-member" id="{html.escape(node.name)}">'
            f'<div class="api-signature-head"><h3><code>{html.escape(signature_for(node))}</code></h3>{badge}</div>'
            f'{doc_to_html(ast.get_docstring(node))}</section>'
        )
    source_rel = source.relative_to(ROOT).as_posix()
    return f'''<section class="content-wrap"><article class="docs-article api-page">
      <div class="eyebrow">API Reference</div>
      <h1>{html.escape(display)}</h1>
      <p class="api-source">Source: <code>{html.escape(source_rel)}</code></p>
      <div class="api-class-doc">{class_doc}</div>
      <h2>Public methods</h2>
      {''.join(method_cards) if method_cards else '<p class="muted">No public methods found.</p>'}
    </article></section>'''


def api_index_body() -> str:
    cards = []
    for slug, (name, source) in API_MAP.items():
        cards.append(f'<a class="api-index-card" href="{slug}/index.html"><span class="api-card-icon">{html.escape(name[:1])}</span><div><strong>{html.escape(name)}</strong><small>{html.escape(source.parent.name)} helper</small></div><b>→</b></a>')
    return f'''<section class="content-wrap"><article class="docs-article">
      <div class="eyebrow">API Reference</div><h1>Public API</h1>
      <p>Source-backed reference pages generated from the current <code>robo_appian</code> package. Use the component guides for usage patterns and these pages for method signatures and docstrings.</p>
      <div class="api-index-grid">{''.join(cards)}</div>
    </article></section>'''


def build_search_index() -> None:
    items = []
    for page in SITE.rglob("index.html"):
        text = re.sub(r"<[^>]+>", " ", page.read_text(encoding="utf-8"))
        text = re.sub(r"\s+", " ", html.unescape(text)).strip()
        rel = page.relative_to(SITE).as_posix()
        m = re.search(r"<title>(.*?)</title>", page.read_text(encoding="utf-8"), re.S)
        title = re.sub(r"\s*·\s*robo-appian$", "", html.unescape(m.group(1))) if m else rel
        items.append({"title": title, "url": rel, "text": text[:1600]})
    import json
    (SITE / "assets" / "search-index.json").write_text(json.dumps(items, ensure_ascii=False), encoding="utf-8")


def build() -> None:
    if SITE.exists():
        shutil.rmtree(SITE)
    (SITE / "assets").mkdir(parents=True)

    # Homepage
    write_page("index.html", "Home", home_body(), "Home", "Reusable Playwright helpers for reliable Appian UI automation.")

    # Markdown-backed content pages
    md_pages = [
        ("getting-started/installation/index.html", "Installation", DOCS / "getting-started" / "installation.md", "Getting Started", "Getting Started"),
        ("getting-started/quick-start/index.html", "Quick Start", DOCS / "getting-started" / "quick-start.md", "Getting Started", "Getting Started"),
        ("guides/components/index.html", "Components", DOCS / "guides" / "components.md", "Components", "Guide"),
        ("guides/development/index.html", "Development", DOCS / "guides" / "development.md", "Guides", "Guide"),
        ("guides/publishing-docs/index.html", "Publishing Docs", DOCS / "guides" / "publishing-docs.md", "Guides", "Guide"),
    ]
    for path, title, source, current, eyebrow in md_pages:
        write_page(path, title, markdown_body(source, eyebrow), current)

    # API pages
    write_page("api/index.html", "API Reference", api_index_body(), "API Reference")
    for slug, (name, source) in API_MAP.items():
        write_page(f"api/{slug}/index.html", name, api_class_page(slug, name, source), "API Reference")

    # Assets
    (SITE / "assets" / "styles.css").write_text(STYLES, encoding="utf-8")
    (SITE / "assets" / "site.js").write_text(SCRIPT, encoding="utf-8")
    (SITE / ".nojekyll").write_text("", encoding="utf-8")
    (SITE / "404.html").write_text(page_shell("Page not found", '<section class="content-wrap"><article class="docs-article"><h1>404</h1><p>The requested page was not found.</p><p><a class="button primary" href="index.html">Back home</a></p></article></section>', "404.html", ""), encoding="utf-8")
    build_search_index()


STYLES = r'''
:root{--blue:#2854d7;--blue2:#173dba;--ink:#10245f;--text:#25324b;--muted:#69758d;--line:#dce5f5;--soft:#f6f9ff;--card:#fff;--shadow:0 12px 35px rgba(36,73,155,.11);--code:#121a2b;--radius:14px}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;font-family:Inter,ui-sans-serif,-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif;color:var(--text);background:#fff;line-height:1.6}a{color:var(--blue);text-decoration:none}a:hover{text-decoration:none}code{font-family:"SFMono-Regular",Consolas,"Liberation Mono",monospace;background:#eef3fb;border-radius:5px;padding:.12em .34em;font-size:.92em}.site-header{position:sticky;top:0;z-index:50;background:linear-gradient(90deg,#2f4cc2,#345bd8);color:#fff;box-shadow:0 1px 0 rgba(255,255,255,.16)}.header-inner{max-width:1320px;margin:auto;height:72px;padding:0 28px;display:flex;align-items:center;gap:34px}.brand{display:flex;align-items:center;gap:11px;color:#fff;font-weight:800;font-size:20px;white-space:nowrap}.brand-mark{width:28px;height:28px;border:2px solid rgba(255,255,255,.9);display:grid;place-items:center;border-radius:8px;font-size:11px}.top-nav{display:flex;align-items:stretch;height:100%;gap:4px}.nav-link{display:flex;align-items:center;padding:0 15px;color:#e9eeff;font-weight:600;font-size:14px;position:relative}.nav-link:hover,.nav-link.active{color:#fff}.nav-link.active:after{content:"";position:absolute;left:14px;right:14px;bottom:0;height:3px;background:#fff;border-radius:3px 3px 0 0}.header-actions{margin-left:auto;display:flex;gap:8px}.search-button,.theme-button{border:1px solid rgba(255,255,255,.18);color:#fff;background:rgba(18,43,135,.45);border-radius:7px;height:40px;padding:0 13px;font:inherit;cursor:pointer}.search-button{min-width:170px;text-align:left}.search-panel{position:fixed;z-index:80;top:72px;left:0;right:0;background:rgba(10,28,86,.96);padding:18px 24px;box-shadow:0 15px 40px rgba(7,24,70,.25)}.search-panel-inner{max-width:900px;margin:auto}.search-panel input{width:100%;border:0;border-radius:8px;padding:13px 15px;font:inherit}.search-results{margin-top:8px;display:grid;gap:5px;max-height:50vh;overflow:auto}.search-results a{display:block;background:#fff;color:var(--ink);padding:10px 12px;border-radius:7px}.hero{background:linear-gradient(145deg,#f7fbff 0,#edf5ff 54%,#f9fbff 100%);border-bottom:1px solid #e7edf7}.hero-grid{max-width:1320px;margin:auto;padding:58px 36px 46px;display:grid;grid-template-columns:1.05fr .95fr;gap:52px;align-items:center}.hero-badges{display:flex;gap:8px;margin-bottom:20px}.hero-badges span{font-size:12px;font-weight:800;border:1px solid #b7c9ff;background:#fff;color:#2e55c5;border-radius:999px;padding:4px 10px}.hero-badges span:nth-child(2){color:#117759;border-color:#a7e2d1}.hero-badges span:nth-child(3){color:#99339d;border-color:#e0afe3}.hero h1{font-size:52px;line-height:1.04;letter-spacing:-.035em;color:#0a2675;margin:0 0 20px}.hero h1 span{color:#214fcb}.hero-lede{font-size:18px;line-height:1.65;max-width:720px;color:#3a4965}.hero-actions{display:flex;gap:12px;flex-wrap:wrap;margin-top:26px}.button{display:inline-flex;align-items:center;justify-content:center;border:1px solid #9fb6ef;color:#234fc8;background:#fff;border-radius:8px;padding:11px 18px;font-weight:800;box-shadow:0 5px 16px rgba(28,68,168,.08)}.button.primary{color:#fff;background:linear-gradient(180deg,#3563dd,#234cc6);border-color:#244bc0}.install-line{margin-top:20px;border:1px solid #d8e2f5;background:#fff;border-radius:9px;display:inline-flex;align-items:center;gap:10px;padding:8px 10px;color:#71809b}.install-line code{background:transparent;color:#13224c}.install-line button{border:0;background:transparent;color:#3155bd;font-weight:700;cursor:pointer}.hero-visual{position:relative;height:330px;min-width:0}.browser-card{position:absolute;right:62px;top:8px;width:300px;height:246px;background:#fff;border:1px solid #c8d8f5;border-radius:12px;box-shadow:var(--shadow);overflow:hidden}.browser-top{height:32px;background:#6c8dbb;display:flex;gap:7px;padding:11px}.browser-top span{width:8px;height:8px;border-radius:50%;background:#ff805c}.browser-top span:nth-child(2){background:#ffc54d}.browser-top span:nth-child(3){background:#42d071}.appian-label{font-weight:800;color:#1a4db9;padding:18px 18px 5px}.skeleton{display:grid;gap:10px;padding:0 18px}.skeleton i{height:13px;background:#e8f0fb;border-radius:5px}.skeleton i:nth-child(2){width:78%}.skeleton i:nth-child(3){width:63%}.flow-card{position:absolute;background:#fff;border:1px solid #c8d8f5;border-radius:12px;box-shadow:var(--shadow);padding:15px;display:flex;flex-direction:column;gap:3px;font-size:13px}.flow-card strong{color:#0e2c79;font-size:15px}.flow-card span{color:#54637e}.flow-card.tests{left:0;top:70px;width:150px}.flow-card.library{left:210px;top:100px;width:170px;align-items:center;text-align:center}.flow-card.playwright{right:0;top:116px;width:130px;text-align:center;border-color:#9fdbc8}.robot{font-size:34px;color:#204fc9}.flow-arrow{position:absolute;color:#2450cb;font-size:28px;font-weight:900}.flow-arrow.one{left:168px;top:130px}.flow-arrow.two{right:137px;top:155px}.section-shell{max-width:1320px;margin:0 auto;padding:34px 36px}.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}.stat-card{display:flex;gap:17px;border:1px solid var(--line);background:#fff;border-radius:12px;padding:20px 22px;box-shadow:0 4px 18px rgba(32,73,150,.04)}.stat-icon{width:48px;height:48px;border-radius:50%;display:grid;place-items:center;flex:0 0 auto;font-size:22px;color:#fff}.purple{background:#793cd3}.green{background:#11ab6e}.blue{background:#2e7cdf}.stat-card div:last-child{display:flex;flex-direction:column}.stat-card strong{font-size:22px;color:#0e2b78;line-height:1.15}.stat-card span{font-weight:700}.stat-card small{color:var(--muted);margin-top:3px}.section-kicker{text-transform:uppercase;letter-spacing:.12em;font-weight:800;font-size:12px;color:#3f65c9}.section-shell h2{font-size:31px;letter-spacing:-.025em;color:#10265d;margin:7px 0 18px}.split-section{display:grid;grid-template-columns:1.05fr .95fr;gap:38px;align-items:start}.feature-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}.feature-card{display:flex;gap:14px;border:1px solid var(--line);border-radius:10px;padding:16px;background:#fff}.feature-card>span{width:38px;height:38px;border-radius:50%;background:#eef4ff;color:#2854d7;display:grid;place-items:center;font-size:20px;flex:0 0 auto}.feature-card strong{color:#102d77}.feature-card p{margin:3px 0 0;color:var(--muted);font-size:14px;line-height:1.45}.code-panel{background:var(--code);color:#e8edf7;border-radius:12px;overflow:hidden;box-shadow:0 18px 42px rgba(9,20,44,.17)}.code-panel-title{display:flex;justify-content:space-between;align-items:center;padding:10px 13px;background:#202b3e;color:#c8d2e4;font-size:13px}.code-panel-title button{border:0;background:transparent;color:#c8d2e4;cursor:pointer}.code-panel pre{margin:0;padding:20px;overflow:auto;min-height:290px}.code-panel code{background:transparent;color:#dbe7ff;padding:0;line-height:1.7}.chips{display:flex;flex-wrap:wrap;gap:10px}.chip{border:1px solid #d5e0f4;background:#f8fbff;border-radius:999px;padding:8px 13px;font-weight:700;font-size:13px;color:#3158bd}.chip:hover{background:#edf4ff;transform:translateY(-1px)}.section-copy{color:var(--muted);max-width:850px}.architecture-flow{display:grid;grid-template-columns:1fr auto 1fr auto 1fr auto 1fr;gap:12px;align-items:center;margin-top:24px}.architecture-flow>div{border:1px solid var(--line);border-radius:10px;padding:15px;background:#fff;display:flex;flex-direction:column}.architecture-flow .highlight{background:#eef4ff;border-color:#b9cdf6}.architecture-flow strong{color:#0d2b77}.architecture-flow span{font-size:13px;color:var(--muted)}.architecture-flow>b{color:#2854d7;font-size:22px}.start-section{padding-bottom:60px}.next-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}.next-grid>a{display:grid;grid-template-columns:auto 1fr auto;align-items:center;gap:14px;border:1px solid var(--line);border-radius:11px;background:#fff;padding:16px;color:var(--text)}.next-grid>a>span{width:42px;height:42px;border-radius:50%;background:#eef4ff;color:#2854d7;display:grid;place-items:center}.next-grid>a div{display:flex;flex-direction:column}.next-grid strong{color:#12317c}.next-grid small{color:var(--muted)}.content-wrap{max-width:1160px;margin:0 auto;padding:44px 36px 70px}.docs-article{max-width:900px}.docs-article .eyebrow{text-transform:uppercase;letter-spacing:.12em;color:#4165c6;font-weight:800;font-size:12px;margin-bottom:8px}.docs-article h1{font-size:43px;letter-spacing:-.03em;line-height:1.08;color:#102864;margin:0 0 20px}.docs-article h2{font-size:28px;color:#17356f;margin-top:42px}.docs-article h3{color:#20417e;margin-top:28px}.docs-article p,.docs-article li{color:#3d4a63}.docs-article pre{background:#111a2a;color:#e4edff;border-radius:10px;padding:18px;overflow:auto;box-shadow:0 8px 26px rgba(7,20,48,.1)}.docs-article pre code{background:transparent;color:inherit;padding:0}.docs-article table{border-collapse:collapse;width:100%}.docs-article th,.docs-article td{border:1px solid var(--line);padding:9px 11px;text-align:left}.docs-article blockquote{border-left:4px solid #6b89e5;margin-left:0;padding:10px 16px;background:#f7f9ff}.api-index-grid{display:grid;grid-template-columns:1fr 1fr;gap:13px;margin-top:28px}.api-index-card{display:grid;grid-template-columns:auto 1fr auto;align-items:center;gap:14px;padding:15px;border:1px solid var(--line);border-radius:10px;background:#fff;color:var(--text)}.api-index-card:hover{border-color:#aac1f1;box-shadow:0 8px 24px rgba(28,64,145,.08)}.api-card-icon{width:40px;height:40px;border-radius:9px;background:#eef4ff;color:#2b54c5;display:grid;place-items:center;font-weight:900}.api-index-card div{display:flex;flex-direction:column}.api-index-card strong{color:#12317c}.api-index-card small{color:var(--muted)}.api-source{background:#f8fbff;border:1px solid var(--line);padding:10px 12px;border-radius:8px}.api-member{border-top:1px solid var(--line);padding:24px 0}.api-member h3{margin:0 0 10px;font-size:18px}.api-signature-head{display:flex;align-items:flex-start;justify-content:space-between;gap:12px}.api-badge{font-size:11px;text-transform:uppercase;letter-spacing:.08em;background:#eef4ff;color:#2b54c5;border-radius:999px;padding:4px 8px;font-weight:800}.api-detail-list{list-style:none;padding:0;display:grid;gap:7px}.api-detail-list li{display:grid;grid-template-columns:minmax(130px,auto) 1fr;gap:12px}.muted{color:var(--muted)!important}.site-footer{border-top:1px solid var(--line);max-width:1320px;margin:0 auto;padding:26px 36px 40px;display:flex;justify-content:space-between;gap:24px;color:var(--muted);font-size:13px}.footer-links{display:flex;gap:18px}@media(max-width:980px){.top-nav{display:none}.hero-grid,.split-section{grid-template-columns:1fr}.hero-visual{height:310px}.stats{grid-template-columns:1fr}.architecture-flow{grid-template-columns:1fr}.architecture-flow>b{transform:rotate(90deg);justify-self:center}.next-grid{grid-template-columns:1fr}.api-index-grid{grid-template-columns:1fr}.hero h1{font-size:44px}}@media(max-width:640px){.header-inner{padding:0 16px}.search-button{min-width:0}.search-button span{display:none}.hero-grid,.section-shell,.content-wrap{padding-left:20px;padding-right:20px}.hero h1{font-size:37px}.feature-grid{grid-template-columns:1fr}.hero-visual{display:none}.site-footer{padding-left:20px;padding-right:20px;flex-direction:column}.api-detail-list li{grid-template-columns:1fr}}
@media(prefers-color-scheme:dark){:root{--text:#d6def0;--muted:#9ca9c0;--line:#263554;--soft:#101827;--card:#111b2e;--ink:#d8e3ff}body{background:#0d1422;color:var(--text)}code{background:#1a2740}.hero{background:linear-gradient(145deg,#101a2d,#111c31);border-bottom-color:#23314d}.stat-card,.feature-card,.next-grid>a,.api-index-card,.architecture-flow>div,.docs-article blockquote{background:#111b2e}.architecture-flow .highlight{background:#17284a}.install-line{background:#111b2e;border-color:#2b3e63}.install-line code{color:#dce6ff}.browser-card,.flow-card{background:#111b2e;border-color:#2d4268}.section-shell h2,.docs-article h1,.docs-article h2,.docs-article h3,.stat-card strong,.feature-card strong,.next-grid strong,.api-index-card strong,.architecture-flow strong{color:#dce7ff}.docs-article p,.docs-article li{color:#c2cce0}.chip{background:#111b2e;border-color:#2a3e63}.site-footer{border-top-color:#263554}.api-source{background:#111b2e}.search-results a{background:#111b2e;color:#dce7ff}}
'''

SCRIPT = r'''
(() => {
  const q = (s, root=document) => root.querySelector(s);
  const qa = (s, root=document) => [...root.querySelectorAll(s)];
  qa('[data-copy]').forEach(btn => btn.addEventListener('click', async () => {
    try { await navigator.clipboard.writeText(btn.dataset.copy || ''); btn.textContent='Copied'; setTimeout(()=>btn.textContent='Copy',1200); } catch (_) {}
  }));
  qa('[data-copy-target]').forEach(btn => btn.addEventListener('click', async () => {
    const target = document.getElementById(btn.dataset.copyTarget); if (!target) return;
    try { await navigator.clipboard.writeText(target.innerText); btn.textContent='Copied'; setTimeout(()=>btn.textContent='Copy',1200); } catch (_) {}
  }));
  const themeBtn=q('[data-theme-toggle]');
  if (themeBtn) themeBtn.addEventListener('click', () => {
    const dark=document.documentElement.dataset.theme==='dark';
    document.documentElement.dataset.theme=dark?'light':'dark';
    if (!dark) document.documentElement.style.colorScheme='dark'; else document.documentElement.style.colorScheme='light';
  });
  const toggle=q('[data-search-toggle]'), panel=q('[data-search-panel]'), input=q('[data-search-input]'), results=q('[data-search-results]');
  let index=null;
  async function loadIndex(){ if(index) return index; const depth=location.pathname.split('/').filter(Boolean).length; let prefix='../'.repeat(Math.max(0,depth-1)); try{index=await (await fetch(prefix+'assets/search-index.json')).json()}catch(_){index=[]} return index; }
  function pagePrefix(){ const parts=location.pathname.split('/').filter(Boolean); return '../'.repeat(Math.max(0, parts.length-1)); }
  if(toggle&&panel&&input){
    toggle.addEventListener('click', async()=>{panel.hidden=!panel.hidden;if(!panel.hidden){await loadIndex();input.focus()}});
    input.addEventListener('input', async()=>{const items=await loadIndex();const term=input.value.trim().toLowerCase();if(!term){results.innerHTML='';return}const matches=items.filter(x=>(x.title+' '+x.text).toLowerCase().includes(term)).slice(0,8);results.innerHTML=matches.map(x=>`<a href="${pagePrefix()}${x.url}"><strong>${x.title}</strong></a>`).join('')||'<div style="color:white;padding:8px">No matches</div>';});
  }
})();
'''

if __name__ == "__main__":
    build()
    print(f"Built GitHub Pages site: {SITE}")
