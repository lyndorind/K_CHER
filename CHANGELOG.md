# Changelog

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