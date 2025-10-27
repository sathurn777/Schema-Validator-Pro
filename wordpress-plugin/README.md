# Schema Validator Pro - WordPress Plugin

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/YOUR_USERNAME/schema-validator-pro/releases)
[![WordPress](https://img.shields.io/badge/wordpress-5.0%2B-blue.svg)](https://wordpress.org/)
[![PHP](https://img.shields.io/badge/php-7.4%2B-blue.svg)](https://www.php.net/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](../LICENSE)

Automatically inject Schema.org JSON-LD structured data into WordPress posts and pages for better SEO and rich search results.

---

## 🎯 Features

- **Automatic Schema Generation** - Generate schema markup with one click
- **9 Schema Types Supported** - Article, Product, Recipe, HowTo, FAQPage, Event, Person, Organization, Course
- **Zero Configuration** - Works out of the box with sensible defaults
- **SEO Optimized** - Follows Google's structured data guidelines
- **Validation Built-in** - Ensures your schema is valid before injection
- **Developer Friendly** - Clean code, hooks, and filters for customization
- **Caching** - Built-in caching for improved performance
- **Logging** - Comprehensive logging for debugging

---

## 📋 Requirements

- **WordPress**: 5.0 or higher
- **PHP**: 7.4 or higher
- **Backend API**: FastAPI service (included in the main package)

---

## 🚀 Installation

### Step 1: Install the WordPress Plugin

#### Option A: Manual Installation

1. Download the plugin ZIP file from the [releases page](https://github.com/YOUR_USERNAME/schema-validator-pro/releases)
2. Log in to your WordPress admin panel
3. Navigate to **Plugins > Add New > Upload Plugin**
4. Choose the ZIP file and click **Install Now**
5. Click **Activate**

#### Option B: From Source

1. Clone the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/schema-validator-pro.git
   cd schema-validator-pro/wordpress-plugin
   ```

2. Copy the `schema-validator-pro` folder to your WordPress plugins directory:
   ```bash
   cp -r schema-validator-pro /path/to/wordpress/wp-content/plugins/
   ```

3. Activate the plugin in WordPress admin panel

### Step 2: Set Up the Backend API

The WordPress plugin requires a backend API service to generate schema markup. Choose one of the following options:

#### Option 1: Local Development

```bash
# Navigate to the project root
cd schema-validator-pro

# Install Python dependencies
pip install -r requirements.txt

# Start the API server
python -m backend.main
```

The API will be available at `http://localhost:8000`

#### Option 2: Docker

```bash
# Navigate to the project root
cd schema-validator-pro

# Build the Docker image
docker build -f config/Dockerfile -t schema-validator-pro .

# Run the container
docker run -p 8000:8000 schema-validator-pro
```

The API will be available at `http://localhost:8000`

#### Option 3: Production Deployment

Deploy the backend API to your server using:
- **Docker + Docker Compose**
- **Kubernetes**
- **Cloud platforms** (AWS, GCP, Azure)
- **VPS with systemd service**

See the main [DEPLOYMENT.md](../docs/DEPLOYMENT.md) for detailed instructions.

### Step 3: Configure the Plugin

1. In WordPress admin, navigate to **Schema Pro > Settings**
2. Enter your backend API endpoint:
   - Local development: `http://localhost:8000`
   - Production: `https://api.yoursite.com`
3. (Optional) Enter your API key if authentication is enabled
4. Click **Save Settings**
5. Verify the API status shows a green checkmark ✓

---

## 📖 Usage

### Generating Schema for a Post

1. Edit any post or page in WordPress
2. Find the **Schema Validator Pro** meta box in the sidebar (or below the editor)
3. Select the schema type (default: Article)
4. Click **Generate Schema**
5. Review the generated JSON-LD in the preview
6. Save or publish your post

The schema will be automatically injected into the `<head>` section of your page.

### Supported Schema Types

| Schema Type | Best For | Example Use Case |
|------------|----------|------------------|
| **Article** | Blog posts, news | Blog articles, news stories |
| **Product** | E-commerce | Product pages, shop items |
| **Recipe** | Food blogs | Cooking recipes, meal plans |
| **HowTo** | Tutorials | Step-by-step guides |
| **FAQPage** | Support pages | FAQ sections, Q&A pages |
| **Event** | Event listings | Conferences, webinars, concerts |
| **Person** | Author pages | Author bios, team members |
| **Organization** | Company pages | About us, company info |
| **Course** | Education | Online courses, training programs |

### Validating Your Schema

After generating schema, validate it using:

- **Google Rich Results Test**: https://search.google.com/test/rich-results
- **Schema.org Validator**: https://validator.schema.org/

---

## 🔧 Configuration

### Settings Page

Navigate to **Schema Pro > Settings** to configure:

- **API Endpoint**: Backend API URL (required)
- **API Key**: Authentication key (optional)
- **Cache Management**: Clear cached schemas
- **API Status**: Check if the backend API is available

### Hooks and Filters

For developers who want to customize the plugin:

#### Filters

```php
// Modify schema data before injection
add_filter('svp_schema_data', function($schema_data, $post_id) {
    // Your custom logic
    return $schema_data;
}, 10, 2);

// Modify API endpoint
add_filter('svp_api_endpoint', function($endpoint) {
    return 'https://custom-api.example.com';
});
```

#### Actions

```php
// Before schema injection
add_action('svp_before_schema_injection', function($schema_data, $post_id) {
    // Your custom logic
}, 10, 2);

// After schema injection
add_action('svp_after_schema_injection', function($schema_data, $post_id) {
    // Your custom logic
}, 10, 2);
```

---

## 🧪 Testing

The plugin includes comprehensive PHPUnit tests:

```bash
# Navigate to the plugin directory
cd wordpress-plugin/schema-validator-pro

# Install Composer dependencies
composer install

# Run tests
./vendor/bin/phpunit
```

**Test Coverage**:
- 18 test files
- 4,319 lines of test code
- Covers: initialization, AJAX, meta box, settings, caching, logging, schema injection

---

## 🐛 Troubleshooting

### API Not Available

**Problem**: API status shows red ✗

**Solutions**:
1. Verify the backend API is running: `curl http://localhost:8000/health`
2. Check the API endpoint URL in Settings
3. Check firewall/network settings
4. Review logs in `wp-content/plugins/schema-validator-pro/logs/`

### Schema Not Appearing

**Problem**: Schema not visible in page source

**Solutions**:
1. Verify you clicked "Generate Schema" and saved the post
2. Check if another plugin is already injecting schema (avoid duplicates)
3. Clear WordPress cache and browser cache
4. Check the post meta: `get_post_meta($post_id, '_svp_schema', true)`

### Permission Denied

**Problem**: Cannot generate schema

**Solutions**:
1. Verify you have permission to edit the post
2. Check WordPress user capabilities
3. Review error logs

---

## 📚 Documentation

- **Main README**: [../README.md](../README.md)
- **API Reference**: [../docs/API_REFERENCE.md](../docs/API_REFERENCE.md)
- **Technical Documentation**: [../docs/TECHNICAL.md](../docs/TECHNICAL.md)
- **Deployment Guide**: [../docs/DEPLOYMENT.md](../docs/DEPLOYMENT.md)

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](../CONTRIBUTING.md) for details.

---

## 📄 License

MIT License - see [LICENSE](../LICENSE) for details

---

## 🔗 Links

- **GitHub Repository**: https://github.com/YOUR_USERNAME/schema-validator-pro
- **Issue Tracker**: https://github.com/YOUR_USERNAME/schema-validator-pro/issues
- **Changelog**: [../CHANGELOG.md](../CHANGELOG.md)

---

**Version**: 1.0.0  
**Author**: Schema Validator Pro Team  
**Last Updated**: 2025-10-27

