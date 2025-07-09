# Changelog

All notable changes to the ConfWatch project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `feature/auth-system` branch for authorization system development

## [v2.2.1] - 2025-07-10

### Fixed
- **ROLLBACK FIXED** - Fixed page refresh issue when clicking rollback button
- Added `type='button'` to all buttons in history form to prevent form submission
- Added `event.preventDefault()` and `event.stopPropagation()` to rollback and copy functions
- Added form submit event handler to prevent form submission on Enter key
- Improved modal dialog event handling with better event prevention
- Fixed rollback functionality in web interface - modal now stays open and works correctly

### Changed
- Improved error handling in web interface
- Added error logging to browser console

## [v2.2.0] - 2025-07-09

### Added
- **Authorization system** with Basic Auth and auto-generated password
- Styled login page (`auth.html`)
- Automatic password generation on first run
- Protected routes with `@requires_auth` decorator
- Login and logout routes

### Changed
- Updated web interface to support authorization
- Modified configuration structure to support authorization
- Updated installer to configure authorization

## [v2.1.7] - 2025-07-09

### Added
- Styled terminal confirmation dialog for rollback operations
- Improved UI for critical operation confirmations

## [v2.1.6] - 2025-07-09

### Fixed
- Support for rollback by short commit hash
- Use original file path in API
- Improved path handling in web interface

## [v2.1.5] - 2025-07-09

### Fixed
- Fixed undefined `filePath` variable error in history display
- Improved web interface stability

## [v2.1.4] - 2025-07-09

### Added
- Rollback functionality in web interface
- API endpoint `/api/rollback` for file rollback
- Rollback integration with web interface

## [v2.1.3] - 2025-07-09

### Added
- Commit hash display in history
- Copy hash button to clipboard
- Improved commit information display

## [v2.1.2] - 2025-07-09

### Fixed
- Sort diff commits by date for correct diff display
- Always show newer version on the right side
- Sort selected commits by date before diff calculation
- Fixed incorrect diff order when selecting commits in random order

## [v2.1.1] - 2025-07-09

### Fixed
- Cleaned history view, show only path and user comment
- CLI: handle empty config gracefully, show helpful message
- Core: robust config parsing for empty/invalid YAML

## [v2.1.0] - 2025-07-09

### Added
- CLI commands for creating snapshots with comments
- Tag and rollback commands in CLI
- Enhanced command line functionality

## [v2.0.1] - 2025-07-09

### Fixed
- Updated license link in README
- Minor documentation fixes

## [v2.0.0] - 2025-07-09

### Added
- **Compare any two snapshots** in web interface
- Terminal checkboxes for commit selection
- Support for short git hashes
- Updated UI and API for version comparison
- Enhanced file history navigation

### Changed
- Updated web interface to support arbitrary version comparison
- Improved API for working with diff between any commits

## [v1.0.0] - 2025-07-09

### Added
- **Command animation** in terminal line
- CLI capabilities demonstration in web interface
- Terminal interface design
- Console-style styling
- Enhanced ASCII art

### Changed
- Complete web interface redesign in terminal style
- Improved visual appeal

## [Pre-v1.0.0] - 2025-07-09

### Added
- **Python version** with modular architecture
- **Bash version** with bash-lib integration
- **Smart installer** with Python/Bash detection
- **Web server** with multiple implementations
- **Documentation** in Russian and English
- **MIT license**

### Changed
- Simplified web server to single `webserver.sh` script
- Removed multiple web server implementations
- Renamed `api.sh` to `webserver.sh` for clarity
- Updated README files to reference single webserver.sh

### Removed
- Removed deprecated configuration and web interface files
- Removed scripts and Python dependencies
- Removed WEB_SERVER_README.md

---

## Types of changes

- **Added** - new features
- **Changed** - changes in existing functionality
- **Deprecated** - features that will be removed soon
- **Removed** - removed features
- **Fixed** - bug fixes
- **Security** - vulnerability fixes

## Links

- [GitHub Repository](https://github.com/mrvi0/conf-watch)
- [Issues](https://github.com/mrvi0/conf-watch/issues)
- [Releases](https://github.com/mrvi0/conf-watch/releases) 