# Translation Files

This directory contains translation files for Schema Validator Pro.

## Available Translations

- **English (en_US)**: Default language (built into the plugin)
- **Template (.pot)**: `schema-validator-pro.pot` - Use this to create new translations

## How to Translate

### Using Poedit (Recommended)

1. Download and install [Poedit](https://poedit.net/)
2. Open `schema-validator-pro.pot` in Poedit
3. Create a new translation for your language
4. Save the `.po` and `.mo` files in this directory
5. Name them: `schema-validator-pro-{locale}.po` and `schema-validator-pro-{locale}.mo`
   - Example: `schema-validator-pro-zh_CN.po` for Simplified Chinese
   - Example: `schema-validator-pro-es_ES.po` for Spanish

### Using Loco Translate (WordPress Plugin)

1. Install the [Loco Translate](https://wordpress.org/plugins/loco-translate/) plugin
2. Go to Loco Translate > Plugins > Schema Validator Pro
3. Click "New Language"
4. Select your language and start translating

### Manual Translation

1. Copy `schema-validator-pro.pot` to `schema-validator-pro-{locale}.po`
2. Edit the `.po` file with a text editor
3. Translate all `msgstr ""` entries
4. Compile to `.mo` using `msgfmt`:
   ```bash
   msgfmt schema-validator-pro-zh_CN.po -o schema-validator-pro-zh_CN.mo
   ```

## Contributing Translations

We welcome translations! To contribute:

1. Create a translation using the methods above
2. Test it in your WordPress installation
3. Submit a pull request with your `.po` and `.mo` files
4. Include your name in the translation credits

## Translation Credits

- **English**: Schema Validator Pro Team
- **Chinese (Simplified)**: [Your Name Here]
- **Spanish**: [Your Name Here]
- **French**: [Your Name Here]

## Need Help?

- [WordPress i18n Documentation](https://developer.wordpress.org/plugins/internationalization/)
- [Poedit Tutorial](https://poedit.net/trac/wiki/Doc)
- [Report Translation Issues](https://github.com/schemavalidatorpro/schema-validator-pro/issues)

