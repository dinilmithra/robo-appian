---
hide:
  - navigation
  - toc
---

<div class="ra-target-home">
  <section class="ra-target-hero">
    <div class="ra-target-copy">
      <div class="ra-target-badges">
        <span>◉ Open Source</span>
        <span>Python Automation Framework for Appian</span>
      </div>
      <h1>Automate Appian.<br><em>Faster. Reliably.</em></h1>
      <p>A reusable Python automation framework for Appian UI automation and testing. Built for readable interactions, stable component reuse, and real-world enterprise test suites.</p>
      <div class="ra-target-actions">
        <a class="ra-target-btn primary" href="getting-started/installation/">🚀&nbsp; Get Started <span>→</span></a>
        <a class="ra-target-btn" href="https://github.com/dinilmithra/robo-appian">◉&nbsp; View on GitHub <span>↗</span></a>
      </div>
      <div class="ra-target-install"><span>pip</span><code>pip install robo-appian</code></div>
    </div>
    <div class="ra-target-art">
      <img src="assets/images/robo-appian-logo-3d.png" alt="robo-appian automation framework robot logo">
      <div class="ra-target-float left one"><b>▶</b><span>Automate<br>Workflows</span></div>
      <div class="ra-target-float left two"><b>✓</b><span>Test<br>Processes</span></div>
      <div class="ra-target-float left three"><b>▥</b><span>Ensure<br>Quality</span></div>
      <div class="ra-target-float right one"><b>⚙</b><span>Reusable<br>Utilities</span></div>
      <div class="ra-target-float right two"><b>▥</b><span>Pytest Ready</span></div>
      <div class="ra-target-float right three"><b>∞</b><span>CI/CD Friendly</span></div>
      <div class="ra-target-float right four"><b>▥</b><span>Scalable</span></div>
    </div>
  </section>

  <section class="ra-target-features" aria-label="robo-appian framework capabilities">
    <article><span class="ico">◇</span><div><strong>Reusable Utilities</strong><p>Common Appian actions, components, and helpers ready to use.</p></div></article>
    <article><span class="ico">◎</span><div><strong>Stable Selectors</strong><p>Readable, label-oriented locators for Appian UI elements.</p></div></article>
    <article><span class="ico">▤</span><div><strong>Pytest Ready</strong><p>Works cleanly with pytest fixtures, assertions, and test projects.</p></div></article>
    <article><span class="ico">ϟ</span><div><strong>Parallel Friendly</strong><p>Designed to work with isolated workers and parallel execution.</p></div></article>
    <article><span class="ico">∞</span><div><strong>CI/CD Friendly</strong><p>Fits Jenkins and modern CI/CD automation pipelines.</p></div></article>
    <article><span class="ico">▥</span><div><strong>Clear Diagnostics</strong><p>Playwright-native behavior works with logs, screenshots, and reports.</p></div></article>
  </section>

  <section class="ra-target-workbench">
    <div class="ra-target-code">
      <div class="ra-target-panel-title"><span>›_ &nbsp; Quick Start</span><span>🐍 Python</span></div>
      <pre><code><span class="ln">1</span> <span class="kw">from</span> robo_automation <span class="kw">import</span> AppianPage
<span class="ln">2</span>
<span class="ln">3</span> <span class="kw">def</span> test_user_options(page: AppianPage):
<span class="ln">4</span>     user_options = page.get_by_attributes(
<span class="ln">5</span>         attributes={<span class="st">"role"</span>: <span class="st">"button"</span>, <span class="st">"aria-label"</span>: <span class="st">"User options"</span>},
<span class="ln">6</span>         excat_match=<span class="kw">True</span>,
<span class="ln">7</span>     )
<span class="ln">8</span>     user_options.to_be_visible()
<span class="ln">9</span>     user_options.click()</code></pre>
    </div>

    <div class="ra-target-architecture">
      <div class="ra-target-panel-title light"><span>♟ &nbsp; Architecture Overview</span><a href="getting-started/concepts/">How it works&nbsp; →</a></div>
      <div class="ra-target-arch-flow">
        <div class="node"><span class="node-icon">▤</span><strong>Test Cases</strong><small>• Pytest tests<br>• Page objects<br>• Custom workflows</small></div>
        <b>→</b>
        <div class="node library"><div class="library-brand"><img src="assets/images/robo-appian-icon.png" alt=""><span><strong>robo-appian</strong><small>Appian Component Layer</small></span></div><ul><li>Appian components</li><li>Label-oriented interactions</li><li>Reusable Appian utilities</li><li>Browser install CLI</li><li>Built on robo-automation</li></ul></div>
        <b>→</b>
        <div class="node"><span class="node-icon">▣</span><strong>robo-automation + Playwright</strong><small>• Generic fixtures<br>• Robo* wrappers<br>• Browser engine</small></div>
      </div>
    </div>
  </section>

  <section class="ra-target-docs">
    <div class="ra-target-docs-head"><h2>▣ &nbsp; Documentation</h2><a href="getting-started/installation/">Explore all docs&nbsp; →</a></div>
    <div class="ra-target-doc-grid">
      <a href="getting-started/installation/"><span>↓</span><div><strong>Installation</strong><small>Set up robo-appian in minutes.</small></div><b>→</b></a>
      <a href="getting-started/concepts/"><span>⚙</span><div><strong>Core Concepts</strong><small>Understand scopes and reusable interactions.</small></div><b>→</b></a>
      <a href="api/"><span>&lt;/&gt;</span><div><strong>Core APIs</strong><small>Browse Appian components and utilities.</small></div><b>→</b></a>
      <a href="getting-started/quick-start/"><span>▧</span><div><strong>Examples</strong><small>Ready-to-use automation patterns.</small></div><b>→</b></a>
      <a href="guides/components/"><span>●</span><div><strong>Best Practices</strong><small>Choose the right component for the control.</small></div><b>→</b></a>
      <a href="getting-started/troubleshooting/"><span>◉</span><div><strong>Troubleshooting</strong><small>Common issues and practical solutions.</small></div><b>→</b></a>
    </div>
  </section>

</div>
