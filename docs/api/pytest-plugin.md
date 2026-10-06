# Pytest Plugin

`robo-appian` registers `robo_appian.pytest_plugin` through the `pytest11` entry-point group. The plugin does not own Playwright browser/context/page lifecycle; that remains in `robo-automation`.

It contributes two Appian-layer fixtures:

- `appian_page`: specializes `robo-automation`'s `robo_page` as `AppianPage`.
- `page`: exposes `appian_page` as the normal public page fixture for Appian consumers.

This provides plug-and-play layering while preserving the dependency direction `robo-automation -> robo-appian -> consumer application`.
