/**
 * Schema.org type constants
 */

export const SCHEMA_CONTEXT = 'https://schema.org';

export const SCHEMA_TYPES = {
  ARTICLE: 'Article',
  PRODUCT: 'Product',
  RECIPE: 'Recipe',
  HOW_TO: 'HowTo',
  FAQ_PAGE: 'FAQPage',
  EVENT: 'Event',
  PERSON: 'Person',
  ORGANIZATION: 'Organization',
  COURSE: 'Course',
} as const;

export type SchemaType = (typeof SCHEMA_TYPES)[keyof typeof SCHEMA_TYPES];

/**
 * Product availability constants
 */
export const PRODUCT_AVAILABILITY = {
  IN_STOCK: 'https://schema.org/InStock',
  OUT_OF_STOCK: 'https://schema.org/OutOfStock',
  PRE_ORDER: 'https://schema.org/PreOrder',
  BACK_ORDER: 'https://schema.org/BackOrder',
  DISCONTINUED: 'https://schema.org/Discontinued',
  LIMITED_AVAILABILITY: 'https://schema.org/LimitedAvailability',
} as const;

/**
 * Event status constants
 */
export const EVENT_STATUS = {
  SCHEDULED: 'https://schema.org/EventScheduled',
  CANCELLED: 'https://schema.org/EventCancelled',
  POSTPONED: 'https://schema.org/EventPostponed',
  RESCHEDULED: 'https://schema.org/EventRescheduled',
  MOVED_ONLINE: 'https://schema.org/EventMovedOnline',
} as const;

/**
 * Event attendance mode constants
 */
export const EVENT_ATTENDANCE_MODE = {
  OFFLINE: 'https://schema.org/OfflineEventAttendanceMode',
  ONLINE: 'https://schema.org/OnlineEventAttendanceMode',
  MIXED: 'https://schema.org/MixedEventAttendanceMode',
} as const;

