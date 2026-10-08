# Appian Date

Use `AppianPage.date(...)` for Appian date fields. A date can be identified by its label, placeholder, or nearby header text.

```python
page.date(label="Required Award Date").fill("10/07/2026")
```

```python
page.date(placeholder="mm/dd/yyyy").fill("10/07/2026")
```

```python
page.date(header="Required Award Date").fill("10/07/2026")
```

`AppianDate` inherits the common textbox operations while preserving date-specific behavior.

::: robo_appian.appian.appian_date.AppianDate
