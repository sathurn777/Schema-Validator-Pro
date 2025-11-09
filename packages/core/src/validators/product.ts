/**
 * Product Schema validator
 */

import type { Product, ValidationResult, ValidationError } from '../types';
import {
  validateBase,
  validateRequired,
  validateRecommended,
  validateUrl,
  validateNumber,
} from './base';
import { SCHEMA_TYPES } from '../constants';

/**
 * Validate Product Schema
 */
export function validateProductSchema(schema: unknown): ValidationResult {
  const errors: ValidationError[] = [];
  const warnings: ValidationError[] = [];

  // Base validation
  const baseResult = validateBase(schema);
  errors.push(...baseResult.errors);
  warnings.push(...baseResult.warnings);

  if (!schema || typeof schema !== 'object') {
    return { valid: false, errors, warnings };
  }

  const productSchema = schema as Partial<Product>;

  // Check @type
  if (productSchema['@type'] !== SCHEMA_TYPES.PRODUCT) {
    errors.push({
      field: '@type',
      message: `@type must be "${SCHEMA_TYPES.PRODUCT}"`,
      severity: 'error',
    });
  }

  // Required fields
  validateRequired(productSchema.name, 'name', errors);

  // Recommended fields
  validateRecommended(
    productSchema.description,
    'description',
    warnings,
    'description is recommended for better SEO'
  );

  validateRecommended(
    productSchema.image,
    'image',
    warnings,
    'image is recommended for rich results in search engines'
  );

  validateRecommended(
    productSchema.offers,
    'offers',
    warnings,
    'offers is recommended to show price information'
  );

  // Validate brand
  if (productSchema.brand) {
    if (typeof productSchema.brand === 'object') {
      const brand = productSchema.brand as unknown as Record<string, unknown>;
      validateRequired(brand.name, 'brand.name', errors);
    }
  }

  // Validate offers
  if (productSchema.offers) {
    const offers = Array.isArray(productSchema.offers)
      ? productSchema.offers
      : [productSchema.offers];

    offers.forEach((offer, index) => {
      if (typeof offer !== 'object' || offer === null) {
        errors.push({
          field: `offers[${index}]`,
          message: 'offer must be an object',
          severity: 'error',
        });
        return;
      }

      const offerObj = offer as unknown as Record<string, unknown>;

      validateRequired(offerObj.price, `offers[${index}].price`, errors);
      validateRequired(offerObj.priceCurrency, `offers[${index}].priceCurrency`, errors);

      if (offerObj.url) {
        validateUrl(offerObj.url, `offers[${index}].url`, errors);
      }
    });
  }

  // Validate aggregate rating
  if (productSchema.aggregateRating) {
    if (typeof productSchema.aggregateRating !== 'object') {
      errors.push({
        field: 'aggregateRating',
        message: 'aggregateRating must be an object',
        severity: 'error',
      });
    } else {
      const rating = productSchema.aggregateRating as unknown as Record<string, unknown>;

      validateRequired(rating.ratingValue, 'aggregateRating.ratingValue', errors);
      validateRequired(rating.reviewCount, 'aggregateRating.reviewCount', errors);

      if (rating.ratingValue) {
        validateNumber(rating.ratingValue, 'aggregateRating.ratingValue', errors, 0, 5);
      }

      if (rating.reviewCount) {
        validateNumber(rating.reviewCount, 'aggregateRating.reviewCount', errors, 1);
      }
    }
  }

  // Validate images
  if (productSchema.image) {
    const images = Array.isArray(productSchema.image)
      ? productSchema.image
      : [productSchema.image];

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

