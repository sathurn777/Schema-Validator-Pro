/**
 * Validation types
 */

export type ValidationSeverity = 'error' | 'warning' | 'info';

export interface ValidationError {
  field: string;
  message: string;
  severity: ValidationSeverity;
  path?: string;
}

export interface ValidationResult {
  valid: boolean;
  errors: ValidationError[];
  warnings: ValidationError[];
  info?: ValidationError[];
}

export interface ValidatorOptions {
  strict?: boolean;
  checkRecommended?: boolean;
}

