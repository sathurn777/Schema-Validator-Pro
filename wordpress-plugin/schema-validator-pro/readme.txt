=== Schema Validator Pro ===
Contributors: schemavalidatorpro
Tags: schema, seo, structured-data, json-ld, rich-snippets
Requires at least: 5.0
Tested up to: 6.4
Requires PHP: 7.4
Stable tag: 1.0.0
License: MIT
License URI: https://opensource.org/licenses/MIT

Automatically inject Schema.org JSON-LD structured data into WordPress posts and pages for better SEO and rich search results.

== Description ==

Schema Validator Pro is a powerful WordPress plugin that automatically generates and injects Schema.org structured data (JSON-LD) into your posts and pages. Improve your SEO and get rich search results on Google, Bing, and other search engines.

= Key Features =

* **Automatic Schema Generation** - Generate schema markup with one click
* **9 Schema Types Supported** - Article, Product, Recipe, HowTo, FAQPage, Event, Person, Organization, Course
* **Zero Configuration** - Works out of the box with sensible defaults
* **SEO Optimized** - Follows Google's structured data guidelines
* **Validation Built-in** - Ensures your schema is valid before injection
* **Developer Friendly** - Clean code, hooks, and filters for customization

= Supported Schema Types =

* **Article** - Blog posts, news articles, and editorial content
* **Product** - E-commerce products with pricing and availability
* **Recipe** - Cooking recipes with ingredients and instructions
* **HowTo** - Step-by-step guides and tutorials
* **FAQPage** - Frequently asked questions
* **Event** - Events, conferences, and webinars
* **Person** - Author profiles and biographical information
* **Organization** - Company and organization information
* **Course** - Educational courses and training programs

= How It Works =

1. Install and activate the plugin
2. Configure the backend API endpoint in Settings
3. Edit any post or page
4. Click "Generate Schema" in the Schema Validator Pro meta box
5. Schema is automatically injected into your page's `<head>` section
6. Validate with Google's Rich Results Test

= Requirements =

* WordPress 5.0 or higher
* PHP 7.4 or higher
* Backend API service (included in the package)

= Backend API =

This plugin requires a backend API service to generate schema markup. The API service is included in the package and can be run locally or deployed to a server.

**Local Development:**
```
cd backend
pip install -r config/requirements.txt
python -m backend.main
```

**Docker:**
```
docker build -f config/Dockerfile -t schema-validator-pro .
docker run -p 8000:8000 schema-validator-pro
```

The default API endpoint is `http://localhost:8000`. You can change this in the plugin settings.

= Privacy =

This plugin sends post content to the configured backend API to generate schema markup. No data is sent to third-party services. The backend API runs on your own infrastructure.

== Installation ==

= Automatic Installation =

1. Log in to your WordPress admin panel
2. Navigate to Plugins > Add New
3. Search for "Schema Validator Pro"
4. Click "Install Now" and then "Activate"

= Manual Installation =

1. Download the plugin ZIP file
2. Log in to your WordPress admin panel
3. Navigate to Plugins > Add New > Upload Plugin
4. Choose the ZIP file and click "Install Now"
5. Activate the plugin

= Backend API Setup =

**Option 1: Local Development**

1. Extract the backend folder from the package
2. Install Python 3.9+ and pip
3. Run: `pip install -r config/requirements.txt`
4. Run: `python -m backend.main`
5. The API will be available at `http://localhost:8000`

**Option 2: Docker**

1. Extract the backend folder from the package
2. Install Docker
3. Run: `docker build -f config/Dockerfile -t schema-validator-pro .`
4. Run: `docker run -p 8000:8000 schema-validator-pro`
5. The API will be available at `http://localhost:8000`

**Option 3: Production Deployment**

Deploy the backend API to your server using:
* Docker + Docker Compose
* Kubernetes
* Cloud platforms (AWS, GCP, Azure)
* VPS with systemd service

= Configuration =

1. Navigate to Schema Pro > Settings in your WordPress admin
2. Enter your backend API endpoint (e.g., `http://localhost:8000` or `https://api.yoursite.com`)
3. Click "Save Settings"

== Frequently Asked Questions ==

= Do I need to install anything besides the WordPress plugin? =

Yes, you need to run the backend API service. The API can run locally (for development) or on a server (for production). See the Installation section for details.

= What Schema types are supported? =

Currently, we support 9 Schema types: Article, Product, Recipe, HowTo, FAQPage, Event, Person, Organization, and Course. More types will be added in future releases.

= Is the schema automatically injected into all posts? =

No, you need to manually generate schema for each post by clicking the "Generate Schema" button in the post editor. This gives you full control over which posts have schema markup.

= Can I edit the generated schema? =

Currently, the plugin generates schema automatically based on your post content. Manual editing is not supported in version 1.0.0, but it's planned for a future release.

= Does this work with Gutenberg and Classic Editor? =

Yes, the plugin works with both Gutenberg (Block Editor) and Classic Editor.

= Will this slow down my website? =

No, the schema is injected as a small JSON-LD script in the `<head>` section. It has minimal impact on page load time.

= Is the generated schema valid? =

Yes, the backend API includes a built-in validator that ensures the generated schema follows Schema.org specifications and Google's guidelines.

= Can I use this with other SEO plugins? =

Yes, Schema Validator Pro is compatible with popular SEO plugins like Yoast SEO, Rank Math, and All in One SEO. However, make sure you don't have duplicate schema markup.

= Is my data sent to third-party services? =

No, all data is sent only to your configured backend API endpoint. No data is sent to external third-party services.

= What happens if the backend API is unavailable? =

If the API is unavailable, the plugin will display an error message in the admin panel. Existing schema markup will continue to work, but you won't be able to generate new schema until the API is back online.

= How do I validate my schema? =

Use Google's Rich Results Test: https://search.google.com/test/rich-results
Or Schema.org Validator: https://validator.schema.org/

= Can I customize the schema generation? =

Yes, developers can use WordPress hooks and filters to customize the schema generation process. Documentation for developers will be available soon.

== Screenshots ==

1. Schema Validator Pro meta box in post editor
2. Settings page with API endpoint configuration
3. Generated schema JSON preview
4. Main admin page with supported schema types
5. Google Rich Results Test validation

== Changelog ==

= 1.0.0 - 2025-10-21 =
* Initial release
* Support for 9 Schema types (Article, Product, Recipe, HowTo, FAQPage, Event, Person, Organization, Course)
* Automatic schema generation from post content
* Built-in validation
* WordPress admin integration
* Backend API with FastAPI
* Docker support
* Comprehensive documentation

== Upgrade Notice ==

= 1.0.0 =
Initial release of Schema Validator Pro. Install the backend API service before activating the plugin.

== Developer Documentation ==

= Hooks and Filters =

**Filters:**

* `svp_schema_data` - Modify schema data before injection
* `svp_api_endpoint` - Modify API endpoint URL
* `svp_schema_types` - Add or remove supported schema types

**Actions:**

* `svp_before_schema_injection` - Runs before schema is injected
* `svp_after_schema_injection` - Runs after schema is injected
* `svp_schema_generated` - Runs after schema is generated

= Example: Customize Schema Data =

```php
add_filter('svp_schema_data', function($schema, $post_id) {
    // Add custom property
    $schema['customProperty'] = 'custom value';
    return $schema;
}, 10, 2);
```

= Example: Add Custom Schema Type =

```php
add_filter('svp_schema_types', function($types) {
    $types['LocalBusiness'] = 'Local Business';
    return $types;
});
```

= Support =

For support, feature requests, and bug reports, please visit:
* GitHub: https://github.com/yourorg/schema-validator-pro
* Documentation: https://docs.schemavalidatorpro.com
* Email: support@schemavalidatorpro.com

== Credits ==

* Built with FastAPI and Python
* Uses Schema.org vocabulary
* Follows WordPress coding standards
* Inspired by the need for better structured data tools

== License ==

This plugin is licensed under the MIT License. See LICENSE file for details.

