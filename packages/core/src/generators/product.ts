/**
 * Product Schema generator
 */

import type { Product, ProductInput, ImageObject } from '../types';
import { SCHEMA_CONTEXT, SCHEMA_TYPES, PRODUCT_AVAILABILITY } from '../constants';
import { normalizeUrl } from '../utils';

/**
 * Generate Product Schema.org JSON-LD
 */
export function generateProductSchema(input: ProductInput): Product {
  const schema: Product = {
    '@context': SCHEMA_CONTEXT,
    '@type': SCHEMA_TYPES.PRODUCT,
    name: input.name,
  };

  // Add optional description
  if (input.description) {
    schema.description = input.description;
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

  // Add optional brand
  if (input.brand) {
    schema.brand = {
      '@type': 'Organization',
      name: input.brand,
    };
  }

  // Add optional SKU, MPN, GTIN
  if (input.sku) {
    schema.sku = input.sku;
  }

  if (input.mpn) {
    schema.mpn = input.mpn;
  }

  if (input.gtin) {
    schema.gtin = input.gtin;
  }

  // Add optional offers
  if (input.price && input.priceCurrency) {
    schema.offers = {
      '@type': 'Offer',
      price: input.price,
      priceCurrency: input.priceCurrency,
      ...(input.availability && {
        availability: input.availability.startsWith('https://')
          ? input.availability
          : PRODUCT_AVAILABILITY.IN_STOCK,
      }),
      ...(input.url && { url: normalizeUrl(input.url) }),
    };
  }

  // Add optional aggregate rating
  if (input.ratingValue && input.reviewCount) {
    schema.aggregateRating = {
      '@type': 'AggregateRating',
      ratingValue: input.ratingValue,
      reviewCount: input.reviewCount,
      bestRating: 5,
      worstRating: 1,
    };
  }

  return schema;
}

