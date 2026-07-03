# Changelog

## [0.7.0](https://github.com/WOT-Lemons/race-monitor-py/compare/v0.6.1...v0.7.0) (2026-07-03)


### ⚠ BREAKING CHANGES

* 429 retries are now bounded by `max_retries` (default 5) instead of retrying forever; callers that relied on infinite retries will now see `RaceMonitorHTTPError(429)` once retries are exhausted. User-supplied httpx `timeout` is now honored — previously it was ignored and every request silently used the 30s default, so callers passing a custom timeout may now observe requests timing out per their own configuration.

### Features

* unify rate limiter, bound 429 retries, harden error handling ([#43](https://github.com/WOT-Lemons/race-monitor-py/issues/43)) ([ce3b1c6](https://github.com/WOT-Lemons/race-monitor-py/commit/ce3b1c62b777a9c3223d2842adb45c47b0c5b9fc))

## [0.6.1](https://github.com/WOT-Lemons/race-monitor-py/compare/v0.6.0...v0.6.1) (2026-06-29)


### Bug Fixes

* **rate-limit:** rotate to another token on 429 instead of re-hammering ([#40](https://github.com/WOT-Lemons/race-monitor-py/issues/40)) ([4034b76](https://github.com/WOT-Lemons/race-monitor-py/commit/4034b76eff10d0905ebc9b808a79951079475e9c))

## [0.6.0](https://github.com/WOT-Lemons/race-monitor-py/compare/v0.5.1...v0.6.0) (2026-06-25)


### Features

* **client:** add multi-token load balancing ([2fae27b](https://github.com/WOT-Lemons/race-monitor-py/commit/2fae27b8a1fc2cbfe809f638121f7b514e82b6c9))
* **protocol:** add StreamingCommand, is_streaming_command, get_streaming_command ([89f27bf](https://github.com/WOT-Lemons/race-monitor-py/commit/89f27bfd915d51d770a634e8975b58d90b3a72a9))

## [0.5.1](https://github.com/WOT-Lemons/race-monitor-py/compare/v0.5.0...v0.5.1) (2026-06-06)


### Bug Fixes

* **deps:** address CVE-2026-45409 and harden uv lock CI ([e3d920f](https://github.com/WOT-Lemons/race-monitor-py/commit/e3d920f0dae2589b61f47eacfe0a88a603d4eef9))

## [0.5.0](https://github.com/WOT-Lemons/race-monitor-py/compare/v0.4.0...v0.5.0) (2026-06-06)


### Features

* **types:** add TypedDict response types for all endpoints ([7f89741](https://github.com/WOT-Lemons/race-monitor-py/commit/7f89741dddffd82da0c089788fce6228adc5cc5b))


### Bug Fixes

* **docs:** expose types submodule so pdoc generates race_monitor/types page ([2984270](https://github.com/WOT-Lemons/race-monitor-py/commit/2984270297e2c039fedfc16d3ea581b1f257c119))

## [0.4.0](https://github.com/WOT-Lemons/race-monitor-py/compare/v0.3.0...v0.4.0) (2026-05-11)


### Features

* Rate limit logging ([#15](https://github.com/WOT-Lemons/race-monitor-py/issues/15)) ([66c0d24](https://github.com/WOT-Lemons/race-monitor-py/commit/66c0d24d39733dab8f9d9ac37648d73d9fdb6945))

## [0.3.0](https://github.com/WOT-Lemons/race-monitor-py/compare/v0.2.0...v0.3.0) (2026-05-10)


### Features

* proactive sliding window rate limiter ([#11](https://github.com/WOT-Lemons/race-monitor-py/issues/11)) ([dd4a2c0](https://github.com/WOT-Lemons/race-monitor-py/commit/dd4a2c03e13467ccb66e9e67898f483946857634))

## [0.2.0](https://github.com/WOT-Lemons/race-monitor-py/compare/v0.1.0...v0.2.0) (2026-05-10)


### Features

* support Python 3.10–3.14 ([#9](https://github.com/WOT-Lemons/race-monitor-py/issues/9)) ([97f12bf](https://github.com/WOT-Lemons/race-monitor-py/commit/97f12bfa32ff875de3f2fc7955bd26e7758a6cf6))

## 0.1.0 (2026-05-10)


### Features

* race-monitor Python client ([#1](https://github.com/WOT-Lemons/race-monitor-py/issues/1)) ([a885327](https://github.com/WOT-Lemons/race-monitor-py/commit/a885327fd2d715f864d49f11e2c4b43f2a53b8fe))
