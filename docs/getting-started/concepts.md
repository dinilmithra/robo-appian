# Core Concepts

`robo-appian` is easiest to use when you understand its role before you start writing tests. It is a **Python component library built on Playwright**. It is not a test framework and it does not own your application workflow.

## The four layers

<div class="ra-layers" aria-label="robo-appian architecture layers">
  <div class="ra-layers-head">
    <span class="ra-layers-kicker">ARCHITECTURE</span>
    <h3>Know what each layer owns</h3>
    <p>Your tests express the workflow. <code>robo-appian</code> provides reusable Appian interactions, Playwright drives the browser, and Appian is the application under test.</p>
  </div>

  <div class="ra-layer-flow">
    <article class="ra-layer-card ra-layer-test">
      <div class="ra-layer-top"><span class="ra-layer-number">1</span><span class="ra-layer-icon" aria-hidden="true">✓</span></div>
      <h4>Your test project</h4>
      <p>Owns application intent and test orchestration.</p>
      <ul>
        <li>Login & navigation</li>
        <li>Workflows & assertions</li>
        <li>Credentials & test data</li>
        <li>Workflow-specific waits</li>
      </ul>
    </article>


    <article class="ra-layer-card ra-layer-robo">
      <div class="ra-layer-top"><span class="ra-layer-number">2</span><span class="ra-layer-icon" aria-hidden="true">⚙</span></div>
      <h4>robo-appian</h4>
      <p>Owns reusable behavior for common Appian controls.</p>
      <ul>
        <li>Label-oriented component lookup</li>
        <li>Fill, click & select operations</li>
        <li>Table, record & region helpers</li>
        <li>Generic component synchronization</li>
      </ul>
    </article>


    <article class="ra-layer-card ra-layer-playwright">
      <div class="ra-layer-top"><span class="ra-layer-number">3</span><span class="ra-layer-icon" aria-hidden="true">↗</span></div>
      <h4>Playwright</h4>
      <p>The browser-automation engine underneath the library.</p>
      <ul>
        <li><code>Scope</code> and locator execution</li>
        <li>Browser interaction</li>
        <li>Locator execution</li>
        <li>Synchronization primitives</li>
      </ul>
    </article>


    <article class="ra-layer-card ra-layer-appian">
      <div class="ra-layer-top"><span class="ra-layer-number">4</span><span class="ra-layer-icon" aria-hidden="true">▦</span></div>
      <h4>Appian</h4>
      <p>The web application UI that is ultimately automated.</p>
      <ul>
        <li>Rendered controls</li>
        <li>Labels & accessible names</li>
        <li>Dynamic UI state</li>
        <li>Application content</li>
      </ul>
    </article>
  </div>

  <div class="ra-layer-summary">
    <div class="ra-layer-summary-icon" aria-hidden="true">i</div>
    <div>
      <strong>The boundary to remember</strong>
      <p><b>Your project</b> owns application-specific behavior. <b>robo-appian</b> owns reusable Appian component behavior. Playwright remains available directly whenever a robo-appian abstraction is not the right fit.</p>
    </div>
  </div>
</div>

!!! important "robo-appian does not replace Playwright"
    Your project still creates and owns the Playwright browser scope, controls authentication and navigation, and can use Playwright directly whenever a robo-appian component is not the right abstraction.

## A label-oriented component model

Many public operations identify Appian controls using the same information a user sees or assistive technology exposes: **visible labels, accessible names, button text, region names, and meaningful scopes**.

```python
from robo_appian import Button, Dropdown, InputText

InputText.fill_by_label(scope, "Request Name", "Example Request")
Dropdown.select(scope, "Request Type", "Travel")
Button.click(scope, "Submit")
```

This is best understood as a **label-oriented component model**: the test expresses the Appian control and user-facing identifier, while the library encapsulates reusable component-specific lookup mechanics.

The phrase is descriptive rather than a formal industry-standard architecture name. The important design goal is to keep consumer tests from depending unnecessarily on Appian-generated DOM details.

!!! note "Labels are the preferred interface, not the only implementation"
    Some Appian layouts cannot be resolved by a normal accessible label. The library therefore includes specialized component methods when a reusable Appian structure requires a different strategy. Use the narrowest public method that matches the rendered control.

## Why this is easier to maintain

A test such as:

```python
Button.click(scope, "Submit")
```

communicates business intent directly. The consumer project does not need to repeat the locator mechanics used to resolve that Appian button.

This does **not** mean labels can never change. If an application renames `Submit` to `Send Request`, the test still needs to change. The benefit is that changes to reusable Appian markup mechanics can usually be handled inside the component library rather than repeated across every consumer workflow.

## Components are static helpers

You normally do not instantiate component classes. Import the component and call the operation you need:

```python
from robo_appian import Button, InputText

InputText.fill_by_label(scope, "Request Name", "Example Request")
Button.click(scope, "Submit")
```

The first argument commonly defines **where to look**. The remaining arguments describe **what to find** and **what to do**.

## `scope`: Playwright `Page` or `Locator`

Public component APIs use `scope` to mean **where robo-appian should search**. A `Scope` is either a Playwright `Page` or a Playwright `Locator`; it is not a separate object created by robo-appian.

| Pass this object | Search boundary |
| --- | --- |
| Playwright `Page` | Entire current document |
| Playwright `Locator` | Only the DOM subtree represented by that locator |

Use the Playwright `Page` when the target is unambiguous across the document:

```python
InputText.fill_by_label(scope, "Request Name", "Example Request")
```

Use a Playwright `Locator` when repeated labels exist or the workflow should stay inside a specific application container:

```python
request_scope = scope.get_by_role("region", name="Request Details")
InputText.fill_by_label(request_scope, "Name", "Example Request")
```

Both calls use the same robo-appian method. Only the Playwright object supplied as the first argument changes. This is why the API calls the parameter `scope` rather than `page`. See the dedicated [Scope reference](../api/scope.md) for the complete explanation.

## Exact matching

Methods that expose an `excat_match` parameter let you control text matching. It is optional and defaults to `False`; pass `True` when an exact label or text match is required.

```python
InputText.fill_by_label(scope, "Name", "Example", excat_match=True)
```

Use exact matching when similar labels could otherwise match the wrong control.

## Waiting and synchronization

Prefer meaningful component state and Playwright synchronization over arbitrary sleeps:

```python
from robo_appian import Button, Text

Button.click(scope, "Submit")
Text.wait_visible(scope, "Created successfully")
```

Generic synchronization needed by a reusable Appian component belongs in `robo-appian`. A wait for a consumer application's workflow or business event belongs in the consumer project.

## Actions and queries

Public methods generally fall into two categories:

- **Actions** interact with the UI: click, fill, select, or wait for a component state.
- **Queries** inspect the UI and return a documented value such as `bool`, `str`, a list, or a Playwright locator.

The API pages show the exact signature, parameter types, defaults, descriptions, and return information for each public method.

## What belongs where?

| Concern | `robo-appian` | Consumer project |
| --- | :---: | :---: |
| Generic Appian control interaction | ✓ | |
| Reusable component lookup mechanics | ✓ | |
| Generic component synchronization | ✓ | |
| Login and application navigation | | ✓ |
| Application workflow orchestration | | ✓ |
| Application-specific labels and rules | | ✓ |
| Assertions and test data | | ✓ |
| Workflow-specific waits | | ✓ |

Next, take the shortest working path through [Quick Start](quick-start.md) or build a complete example in [Your First Test](first-test.md).
