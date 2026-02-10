# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Security
- Updated Next.js from 14.0.0 to 15.0.8 to fix DoS vulnerability in HTTP request deserialization (CVE-2024-XXXX)
- Updated aiohttp from 3.9.1 to 3.13.3 to fix zip bomb vulnerability, directory traversal, and malformed POST DoS
- Updated fastapi from 0.104.1 to 0.109.1 to fix Content-Type Header ReDoS vulnerability

### Added
- Initial monorepo structure
- Core service architecture
- Package structure for shared libraries
- Development environment setup
- Docker Compose configurations
- Makefile for common operations
- Documentation structure

## [0.1.0] - 2026-02-10

### Added
- Project initialization
- Repository structure
- Basic documentation

---

## Release Types

- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** for vulnerability fixes

## Versioning

This project uses Semantic Versioning:
- **MAJOR** version for incompatible API changes
- **MINOR** version for new functionality in a backward compatible manner
- **PATCH** version for backward compatible bug fixes
