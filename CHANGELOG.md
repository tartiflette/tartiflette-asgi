# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Support for `starlette>=0.12` (previously `>=0.12.0b3`).
- Tartiflette is now installed too when installing `tartiflette-starlette`.

### Changed

- The default `path` is now `""` (previously `"/"`).
- The request is now accessible in the GraphQL context via `context["req"]` (previously `context["request"]`).
- If no error occurred, the `errors` field is not present in the response anymore (previously was `None`).

### Fixed

- More robust URL matching on `TartifletteApp`.

### [0.1.1]

Released: 2019-04-28.

### Fixed

- Add missing `graphiql.html` package asset.

## [0.1.0]

Released: 2019-04-26.

### Added

Features:

- `TartifletteApp` ASGI application.
- Built-in GraphiQL client.

Project-related additions:

- Package setup.
- Changelog.
- Contributing guide.
- README and documentation.

[unreleased]: https://github.com/tartiflette/tartiflette-starlette/compare/0.1.1...HEAD
[0.1.1]: https://github.com/tartiflette/tartiflette-starlette/compare/0.1.0...0.1.1
[0.1.0]: https://github.com/tartiflette/tartiflette-starlette/compare/5a1ecf...0.1.0
