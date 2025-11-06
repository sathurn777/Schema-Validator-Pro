# Changelog

All notable changes to Schema Validator Pro will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2025-11-06

### Security
- **Fixed SQL injection vulnerability** in cache clearing function
  - Now using `$wpdb->prepare()` with parameterized queries
  - Added `svp_esc_like()` helper function for proper LIKE wildcard escaping
  - Affects: Settings page cache clear and post update cache clear

### Added
- **Created uninstall.php** for proper plugin cleanup
  - Removes all plugin options on uninstall
  - Deletes all post meta (`_svp_*`)
  - Clears all transient cache
  - Removes log files and directory
  
### Improved
- **Enhanced log file security** with multiple protection layers
  - Improved .htaccess with explicit file type blocking
  - Added index.php to prevent directory listing
  - Added README.txt with Nginx configuration instructions
  - Now supports both Apache and Nginx servers

### Performance
- **Optimized cache clearing** - 18x faster
  - Reduced from 18 database queries to 1 single query
  - Changed from loop-based deletion to SQL LIKE pattern matching
  - Affects: Post update cache clearing for all schema types

### Changed
- Updated version number to 1.0.1 in all files
- Improved database query sanitization throughout the plugin
- Better WordPress coding standards compliance

### Technical Details
- All 212 unit tests passing
- Code coverage: 84.04%
- No breaking changes - fully backward compatible

## [1.0.0] - 2025-11-05

### Added
- Initial release of Schema Validator Pro
- Support for 9 Schema.org types:
  - Article
  - Product
  - Recipe
  - HowTo
  - FAQPage
  - Event
  - Person
  - Organization
  - Course
- Automatic schema generation via API
- Smart caching system with 1-hour expiration
- Meta box integration in post editor
- Settings page for API configuration
- Comprehensive logging system with rotation
- 212 unit tests with 87.52% code coverage
- Complete documentation and examples
- WordPress 5.0+ compatibility
- PHP 7.4+ compatibility

### Features
- One-click schema generation
- Automatic schema injection into page head
- Cache fallback when API is unavailable
- Structured logging (JSON format)
- Log file rotation (10MB limit)
- Internationalization (i18n) support
- Developer-friendly hooks and filters
- Clean, well-documented code

---

## Upgrade Notice

### 1.0.1
This is a security and performance patch. Recommended for all users. Fixes SQL injection vulnerability and improves cache clearing performance by 18x. No breaking changes.

### 1.0.0
Initial release. Install and configure API endpoint in Settings > Schema Validator Pro.

---

## Links
- [GitHub Repository](https://github.com/sathurn777/Schema-Validator-Pro)
- [Documentation](https://github.com/sathurn777/Schema-Validator-Pro#readme)
- [Report Issues](https://github.com/sathurn777/Schema-Validator-Pro/issues)

