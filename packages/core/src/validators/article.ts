/**
 * Article Schema validator
 */

import type { ArticleSchema, ValidationResult, ValidationError } from '../types';
import {
  validateBase,
  validateRequired,
  validateRecommended,
  validateUrl,
  validateDate,
} from './base';
import { SCHEMA_TYPES } from '../constants';

/**
 * Validate Article Schema
 */
export function validateArticleSchema(schema: unknown): ValidationResult {
  const errors: ValidationError[] = [];
  const warnings: ValidationError[] = [];

  // Base validation
  const baseResult = validateBase(schema);
  errors.push(...baseResult.errors);
  warnings.push(...baseResult.warnings);

  if (!schema || typeof schema !== 'object') {
    return { valid: false, errors, warnings };
  }

  const articleSchema = schema as Partial<ArticleSchema>;

  // Check @type
  if (articleSchema['@type'] !== SCHEMA_TYPES.ARTICLE) {
    errors.push({
      field: '@type',
      message: `@type must be "${SCHEMA_TYPES.ARTICLE}"`,
      severity: 'error',
    });
  }

  // Required fields
  validateRequired(articleSchema.headline, 'headline', errors);
  validateRequired(articleSchema.author, 'author', errors);

  // Validate author
  if (articleSchema.author) {
    if (typeof articleSchema.author !== 'object') {
      errors.push({
        field: 'author',
        message: 'author must be an object',
        severity: 'error',
      });
    } else {
      const author = articleSchema.author as unknown as Record<string, unknown>;
      validateRequired(author.name, 'author.name', errors);

      if (author.url) {
        validateUrl(author.url, 'author.url', errors);
      }
    }
  }

  // Recommended fields
  validateRecommended(
    articleSchema.datePublished,
    'datePublished',
    warnings,
    'datePublished is recommended for better SEO and rich results'
  );

  validateRecommended(
    articleSchema.image,
    'image',
    warnings,
    'image is recommended for rich results in search engines'
  );

  validateRecommended(
    articleSchema.description,
    'description',
    warnings,
    'description is recommended for better SEO'
  );

  // Validate optional fields
  if (articleSchema.datePublished) {
    validateDate(articleSchema.datePublished, 'datePublished', errors);
  }

  if (articleSchema.dateModified) {
    validateDate(articleSchema.dateModified, 'dateModified', errors);
  }

  if (articleSchema.url) {
    validateUrl(articleSchema.url, 'url', errors);
  }

  if (articleSchema.mainEntityOfPage) {
    validateUrl(articleSchema.mainEntityOfPage, 'mainEntityOfPage', errors);
  }

  // Validate publisher
  if (articleSchema.publisher) {
    if (typeof articleSchema.publisher !== 'object') {
      errors.push({
        field: 'publisher',
        message: 'publisher must be an object',
        severity: 'error',
      });
    } else {
      const publisher = articleSchema.publisher as unknown as Record<string, unknown>;
      validateRequired(publisher.name, 'publisher.name', errors);

      if (publisher.url) {
        validateUrl(publisher.url, 'publisher.url', errors);
      }

      if (publisher.logo) {
        if (typeof publisher.logo === 'object') {
          const logo = publisher.logo as unknown as Record<string, unknown>;
          validateUrl(logo.url, 'publisher.logo.url', errors);
        }
      }
    }
  }

  // Validate images
  if (articleSchema.image) {
    const images = Array.isArray(articleSchema.image)
      ? articleSchema.image
      : [articleSchema.image];

    images.forEach((img, index) => {
      if (typeof img === 'object' && img !== null) {
        const imageObj = img as unknown as Record<string, unknown>;
        validateUrl(imageObj.url, `image[${index}].url`, errors);
      }
    });
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings,
  };
}

