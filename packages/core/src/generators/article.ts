/**
 * Article Schema generator
 */

import type { ArticleInput, ArticleSchema, ImageObject } from '../types';
import { SCHEMA_CONTEXT, SCHEMA_TYPES } from '../constants';
import { normalizeUrl } from '../utils';

/**
 * Generate Article Schema.org JSON-LD
 */
export function generateArticleSchema(input: ArticleInput): ArticleSchema {
  const schema: ArticleSchema = {
    '@context': SCHEMA_CONTEXT,
    '@type': SCHEMA_TYPES.ARTICLE,
    headline: input.headline,
    author: {
      '@type': 'Person',
      name: input.authorName,
      ...(input.authorUrl && { url: normalizeUrl(input.authorUrl) }),
    },
  };

  // Add optional description
  if (input.description) {
    schema.description = input.description;
  }

  // Add optional dates
  if (input.datePublished) {
    schema.datePublished = input.datePublished;
  }

  if (input.dateModified) {
    schema.dateModified = input.dateModified;
  }

  // Add optional article body
  if (input.articleBody) {
    schema.articleBody = input.articleBody;
  }

  // Add optional URL
  if (input.url) {
    schema.url = normalizeUrl(input.url);
    schema.mainEntityOfPage = normalizeUrl(input.url);
  }

  // Add optional images
  if (input.image) {
    const images = Array.isArray(input.image) ? input.image : [input.image];
    schema.image = images.map(
      (img): ImageObject => ({
        '@type': 'ImageObject',
        url: normalizeUrl(img),
      })
    );

    // If only one image, use object instead of array
    if (schema.image.length === 1) {
      schema.image = schema.image[0];
    }
  }

  // Add optional publisher
  if (input.publisher) {
    schema.publisher = {
      '@type': 'Organization',
      name: input.publisher.name,
      ...(input.publisher.url && { url: normalizeUrl(input.publisher.url) }),
      ...(input.publisher.logo && {
        logo: {
          '@type': 'ImageObject',
          url: normalizeUrl(input.publisher.logo),
        },
      }),
    };
  }

  return schema;
}

