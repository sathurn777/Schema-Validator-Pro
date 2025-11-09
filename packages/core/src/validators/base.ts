/**
 * Base validator functions
 */

import type { BaseSchema, ValidationResult, ValidationError } from '../types';
import { SCHEMA_CONTEXT } from '../constants';

/**
 * Validate base Schema.org properties
 */
export function validateBase(schema: unknown): ValidationResult {
  const errors: ValidationError[] = [];
  const warnings: ValidationError[] = [];

  // Check if schema is an object
  if (!schema || typeof schema !== 'object') {
    errors.push({
      field: 'schema',
      message: 'Schema must be an object',
      severity: 'error',
    });
    return { valid: false, errors, warnings };
  }

  const baseSchema = schema as Partial<BaseSchema>;

  // Check @context
  if (!baseSchema['@context']) {
    errors.push({
      field: '@context',
      message: '@context is required',
      severity: 'error',
    });
  } else if (baseSchema['@context'] !== SCHEMA_CONTEXT) {
    errors.push({
      field: '@context',
      message: `@context must be "${SCHEMA_CONTEXT}"`,
      severity: 'error',
    });
  }

  // Check @type
  if (!baseSchema['@type']) {
    errors.push({
      field: '@type',
      message: '@type is required',
      severity: 'error',
    });
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings,
  };
}

/**
 * Validate required field
 */
export function validateRequired(
  value: unknown,
  fieldName: string,
  errors: ValidationError[]
): void {
  if (!value || (typeof value === 'string' && value.trim() === '')) {
    errors.push({
      field: fieldName,
      message: `${fieldName} is required`,
      severity: 'error',
    });
  }
}

/**
 * Validate recommended field
 */
export function validateRecommended(
  value: unknown,
  fieldName: string,
  warnings: ValidationError[],
  message?: string
): void {
  if (!value || (typeof value === 'string' && value.trim() === '')) {
    warnings.push({
      field: fieldName,
      message: message || `${fieldName} is recommended for better SEO`,
      severity: 'warning',
    });
  }
}

/**
 * Validate URL field
 */
export function validateUrl(
  value: unknown,
  fieldName: string,
  errors: ValidationError[]
): void {
  if (!value) return;

  if (typeof value !== 'string') {
    errors.push({
      field: fieldName,
      message: `${fieldName} must be a string`,
      severity: 'error',
    });
    return;
  }

  try {
    new URL(value);
  } catch {
    errors.push({
      field: fieldName,
      message: `${fieldName} must be a valid URL`,
      severity: 'error',
    });
  }
}

/**
 * Validate date field
 */
export function validateDate(
  value: unknown,
  fieldName: string,
  errors: ValidationError[]
): void {
  if (!value) return;

  if (typeof value !== 'string') {
    errors.push({
      field: fieldName,
      message: `${fieldName} must be a string`,
      severity: 'error',
    });
    return;
  }

  const date = new Date(value);
  if (isNaN(date.getTime())) {
    errors.push({
      field: fieldName,
      message: `${fieldName} must be a valid date`,
      severity: 'error',
    });
  }
}

/**
 * Validate number field
 */
export function validateNumber(
  value: unknown,
  fieldName: string,
  errors: ValidationError[],
  min?: number,
  max?: number
): void {
  if (!value) return;

  if (typeof value !== 'number') {
    errors.push({
      field: fieldName,
      message: `${fieldName} must be a number`,
      severity: 'error',
    });
    return;
  }

  if (min !== undefined && value < min) {
    errors.push({
      field: fieldName,
      message: `${fieldName} must be at least ${min}`,
      severity: 'error',
    });
  }

  if (max !== undefined && value > max) {
    errors.push({
      field: fieldName,
      message: `${fieldName} must be at most ${max}`,
      severity: 'error',
    });
  }
}

