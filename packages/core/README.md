# @schema-validator-pro/core

Core Schema.org JSON-LD generator and validator library.

## Features

- ✅ Generate Schema.org JSON-LD markup for 9 types
- ✅ Validate Schema.org markup
- ✅ TypeScript support with full type definitions
- ✅ Zero dependencies
- ✅ Tree-shakeable ESM modules

## Supported Schema Types

- Article
- Product
- Recipe
- HowTo
- FAQPage
- Event
- Person
- Organization
- Course

## Installation

```bash
pnpm add @schema-validator-pro/core
```

## Usage

### Generate Article Schema

```typescript
import { generateArticleSchema } from '@schema-validator-pro/core';

const schema = generateArticleSchema({
  headline: 'My Article Title',
  authorName: 'John Doe',
  description: 'Article description',
  datePublished: '2025-11-06',
});

console.log(JSON.stringify(schema, null, 2));
```

### Validate Schema

```typescript
import { validateArticleSchema } from '@schema-validator-pro/core';

const result = validateArticleSchema(schema);

if (result.valid) {
  console.log('Schema is valid!');
} else {
  console.error('Validation errors:', result.errors);
}
```

## Development

```bash
# Install dependencies
pnpm install

# Build
pnpm build

# Test
pnpm test

# Test with coverage
pnpm test:coverage

# Lint
pnpm lint
```

## License

MIT

