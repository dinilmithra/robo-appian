---
hide:
  - navigation
  - toc
---

<div class="ra-home">
  <section class="ra-hero">
    <div class="ra-hero-copy">
      <div class="ra-badges" aria-label="Technology stack">
        <span class="ra-badge ra-badge-python">Python</span>
        <span class="ra-badge ra-badge-playwright">Playwright</span>
        <span class="ra-badge ra-badge-appian">Appian</span>
      </div>

      <h1><span>Readable Appian UI automation</span><span>built on Playwright</span></h1>

      <p class="ra-hero-lead"><strong>robo-appian</strong> is a Python component library built on top of Playwright for automating Appian web applications. It provides reusable, label-oriented interactions for common Appian controls so tests stay readable and less coupled to Appian's generated HTML structure.</p>

      <div class="ra-hero-actions">
        <a class="md-button md-button--primary" href="getting-started/installation/">Get Started <span aria-hidden="true">→</span></a>
        <a class="md-button" href="getting-started/concepts/">How It Works</a>
        <a class="md-button" href="api/">Browse API</a>
      </div>
    </div>

    <div class="ra-hero-visual" aria-label="robo-appian architecture">
      <div class="ra-arch-stage">
        <div class="ra-flow-node ra-tests-node">
          <strong>Tests</strong>
          <span>Application flows</span>
          <span>Assertions</span>
          <span>Business rules</span>
          <span>Test data</span>
        </div>

        <div class="ra-flow-arrow" aria-hidden="true">→</div>

        <div class="ra-flow-node ra-robo-node">
          <img src="assets/images/robo-appian-icon.png" alt="" aria-hidden="true">
          <strong>robo-appian</strong>
          <span>Label-oriented Appian component helpers</span>
        </div>

        <div class="ra-flow-arrow" aria-hidden="true">→</div>

        <div class="ra-flow-node ra-appian-node">
          <div class="ra-appian-browser" aria-hidden="true"><i></i><i></i><i></i></div>
          <strong>Appian</strong>
          <span>Web application UI</span>
        </div>
      </div>
      <p class="ra-flow-caption">Tests call robo-appian. robo-appian uses Playwright underneath to locate and interact with the Appian UI.</p>
    </div>
  </section>

  <section class="ra-section ra-model-section">
    <div class="ra-model-heading">
      <span class="ra-eyebrow">SIMPLE, MAINTAINABLE TESTS</span>
      <h2>Write what the user sees—<em>not how the DOM happens to look</em></h2>
      <p>robo-appian identifies Appian controls primarily through user-facing labels, accessible names, visible text, and meaningful scopes where supported. Locator mechanics stay inside reusable components instead of being repeated throughout consumer tests.</p>
    </div>

    <div class="ra-model-grid ra-model-grid-polished">
      <div class="ra-code-card ra-code-card-polished">
        <div class="ra-code-bar"><i></i><i></i><i></i><strong>test_request.py</strong><span aria-hidden="true">↗</span></div>
        <div class="ra-code-lines" aria-label="Example robo-appian test code">
          <div><b>1</b><code><span class="ra-code-key">from</span> robo_appian <span class="ra-code-key">import</span> Button, Dropdown, InputText</code></div>
          <div><b>2</b><code>&nbsp;</code></div>
          <div><b>3</b><code>InputText.fill_by_label(scope, <span class="ra-code-str">"Request Name"</span>, <span class="ra-code-str">"Example"</span>)</code></div>
          <div><b>4</b><code>Dropdown.select(scope, <span class="ra-code-str">"Request Type"</span>, <span class="ra-code-str">"Travel"</span>)</code></div>
          <div><b>5</b><code>Button.click(scope, <span class="ra-code-str">"Submit"</span>)</code></div>
        </div>
        <div class="ra-code-insight">
          <span class="ra-insight-icon" aria-hidden="true">●</span>
          <div><strong>Readable and intention-driven</strong><p>Your test reads like a user interaction: name the Appian control, provide the visible label, and express the action.</p></div>
        </div>
      </div>

      <div class="ra-model-points ra-model-points-polished">
        <article class="ra-step ra-step-blue">
          <div class="ra-step-number">1</div><div class="ra-step-icon" aria-hidden="true">≡</div>
          <div><strong>Express intent</strong><p>Name the Appian control and the action your test wants to perform using labels and visible text.</p></div>
        </article>
        <article class="ra-step ra-step-green">
          <div class="ra-step-number">2</div><div class="ra-step-icon" aria-hidden="true">⚙</div>
          <div><strong>Reuse component logic</strong><p>robo-appian applies common Appian lookup and interaction behavior in one reusable place.</p></div>
        </article>
        <article class="ra-step ra-step-purple">
          <div class="ra-step-number">3</div><div class="ra-step-icon" aria-hidden="true">➤</div>
          <div><strong>Delegate browser interaction</strong><p>robo-appian uses Playwright underneath to perform the actual browser interaction with the Appian UI.</p></div>
        </article>
      </div>
    </div>

    <div class="ra-maintainability-callout">
      <div class="ra-info-icon" aria-hidden="true">i</div>
      <div><strong>Why this is more maintainable</strong><p>Consumer tests generally avoid owning CSS, XPath, generated IDs, and other Appian DOM details. Labels and accessibility semantics can still change, but lookup strategy stays centralized in the library instead of being scattered across workflows.</p></div>
    </div>
  </section>

  <section class="ra-section ra-component-section">
    <div class="ra-component-heading">
      <span class="ra-eyebrow">CHOOSE A COMPONENT</span>
      <h2>Pick the Appian control. <em>robo-appian handles the interaction.</em></h2>
      <p>Start with the helper that matches what the user sees. Each component keeps common Appian lookup and interaction behavior in one reusable place.</p>
    </div>

    <div class="ra-component-explorer">
      <a class="ra-component-card ra-component-primary" href="api/button/">
        <div class="ra-component-icon" aria-hidden="true">B</div>
        <div class="ra-component-copy"><span class="ra-component-type">ACTION</span><strong>Button</strong><p>Click, wait for, and inspect Appian button controls.</p></div>
        <span class="ra-component-arrow" aria-hidden="true">→</span>
      </a>
      <a class="ra-component-card" href="api/input-text/">
        <div class="ra-component-icon" aria-hidden="true">T</div>
        <div class="ra-component-copy"><span class="ra-component-type">INPUT</span><strong>InputText</strong><p>Fill, clear, and inspect text inputs by label.</p></div>
        <span class="ra-component-arrow" aria-hidden="true">→</span>
      </a>
      <a class="ra-component-card" href="api/dropdown/">
        <div class="ra-component-icon" aria-hidden="true">⌄</div>
        <div class="ra-component-copy"><span class="ra-component-type">SELECTION</span><strong>Dropdown</strong><p>Select values from standard Appian dropdown controls.</p></div>
        <span class="ra-component-arrow" aria-hidden="true">→</span>
      </a>
      <a class="ra-component-card" href="api/search-dropdown/">
        <div class="ra-component-icon" aria-hidden="true">⌕</div>
        <div class="ra-component-copy"><span class="ra-component-type">SEARCH + SELECT</span><strong>SearchDropdown</strong><p>Search and choose values from dynamic option lists.</p></div>
        <span class="ra-component-arrow" aria-hidden="true">→</span>
      </a>
      <a class="ra-component-card" href="api/table/">
        <div class="ra-component-icon" aria-hidden="true">▦</div>
        <div class="ra-component-copy"><span class="ra-component-type">DATA</span><strong>Table</strong><p>Read rows, inspect values, and interact with tabular content.</p></div>
        <span class="ra-component-arrow" aria-hidden="true">→</span>
      </a>
      <a class="ra-component-card" href="api/record-list/">
        <div class="ra-component-icon" aria-hidden="true">≡</div>
        <div class="ra-component-copy"><span class="ra-component-type">RECORDS</span><strong>RecordList</strong><p>Work with repeated record content and record-oriented results.</p></div>
        <span class="ra-component-arrow" aria-hidden="true">→</span>
      </a>
      <a class="ra-component-card" href="api/region/">
        <div class="ra-component-icon" aria-hidden="true">□</div>
        <div class="ra-component-copy"><span class="ra-component-type">SCOPE</span><strong>Region</strong><p>Limit interactions to a named area of the Appian interface.</p></div>
        <span class="ra-component-arrow" aria-hidden="true">→</span>
      </a>

      <a class="ra-component-all" href="api/">
        <div>
          <span class="ra-component-type">API REFERENCE</span>
          <strong>Need a different control?</strong>
          <p>Browse every available component, exact signatures, parameters, defaults, and return values.</p>
        </div>
        <span>Explore all API areas <b aria-hidden="true">→</b></span>
      </a>
    </div>
  </section>

  <section class="ra-section ra-boundary-section">
    <div class="ra-section-heading compact">
      <span>SEPARATION OF CONCERNS</span>
      <h2>Keep the library generic and the application logic in your tests</h2>
    </div>
    <div class="ra-boundary-grid">
      <article>
        <div class="ra-boundary-title yes">✓ <strong>robo-appian</strong></div>
        <ul>
          <li>Generic Appian component interactions</li>
          <li>Reusable lookup and locator mechanics</li>
          <li>Common component synchronization</li>
          <li>Reusable scope-based lookup</li>
        </ul>
      </article>
      <article>
        <div class="ra-boundary-title project">→ <strong>Your test project</strong></div>
        <ul>
          <li>Login, navigation, and business workflows</li>
          <li>Application-specific labels and rules</li>
          <li>Assertions, credentials, and test data</li>
          <li>Workflow-specific waits and environment setup</li>
        </ul>
      </article>
    </div>
  </section>

  <section class="ra-section ra-onboard-section">
    <div class="ra-section-heading compact">
      <span>NEW TO ROBO-APPIAN?</span>
      <h2>Go from installation to a useful test in four steps</h2>
    </div>
    <div class="ra-onboard-grid">
      <a href="getting-started/installation/"><b>01</b><strong>Install</strong><span>pip or Poetry, then install Chromium</span></a>
      <a href="getting-started/concepts/"><b>02</b><strong>Understand the model</strong><span>Scopes, labels, Playwright, and project boundaries</span></a>
      <a href="getting-started/first-test/"><b>03</b><strong>Build your first test</strong><span>Use robo-appian inside a normal Playwright test flow</span></a>
      <a href="api/"><b>04</b><strong>Use the API Reference</strong><span>Exact signatures, defaults, parameters, and return values</span></a>
    </div>
  </section>
</div>
