# AppianBrowserContext

`AppianBrowserContext` is the Appian specialization of the generic browser context lifecycle. It creates and exposes `AppianPage` instances so application projects can remain on the Appian abstraction boundary.

```python
from robo_appian import AppianBrowserContext
```

Application projects should normally consume the pytest-managed page fixture rather than construct contexts directly.
