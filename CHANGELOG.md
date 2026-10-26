# Changelog

## [1.3.3] - 2026-10-26
### Fixed
- Підпис образу cosign виконується у форматі, сумісному з Docker Hub (без Referrers API)

## [1.3.2] - 2026-10-26
### Fixed
- Воркфлоу публікації образу: виправлено версію cosign-installer (v4.1.2)
- Сповіщення про публікацію образу налаштовано через інтеграцію GitHub для Slack

## [1.3.1] - 2026-10-26
### Added
- Підпис образу cosign (keyless) та перевірка підпису у воркфлоу публікації
- Сповіщення про публікацію образу в Slack
- Планове та ручне сканування образу (Trivy, Grype, Snyk) зі звітами SARIF у Code Scanning

## [1.3.0] - 2026-10-26
### Added
- Dockerfile та .dockerignore для збірки контейнерного образу
- Воркфлоу публікації образу в Docker Hub при створенні релізу

## [1.2.0] - 2026-10-25
### Added
- REST API на FastAPI (`/health`, `/version`, `/hello/{name}`, `/add`, `/divide`) і тести до нього
- Керування залежностями через uv (`uv.lock`)
- Dependabot для GitHub Actions та uv
### Changed
- Оновлено версії GitHub Actions (checkout v7, upload-artifact v7, setup-uv v10)
- Воркфлоу збірки й релізу використовують uv
### Fixed
- Виправлення зауважень викладача: REST-додаток, uv у воркфлоу, актуальні версії actions
- Release workflow більше не падає, якщо тег уже існує

## [1.1.0] - 2026-10-08
### Added
- Python-пакет `k_cher` з функцією `hello`
- Воркфлоу збірки пакету на Pull Request (артефакти + SHA-256)
- Автоматичний реліз при злитті в `main`

## [1.0.0]
- Initial setup
- Додано README.md
- Додано Issue та Pull Request шаблони