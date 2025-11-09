/**
 * Base Schema.org types
 */

export interface BaseSchema {
  '@context': 'https://schema.org';
  '@type': string;
}

/**
 * Person Schema
 */
export interface Person {
  '@type': 'Person';
  name: string;
  url?: string;
  image?: ImageObject | string;
  email?: string;
  telephone?: string;
  jobTitle?: string;
  affiliation?: Organization;
}

export interface PersonInput {
  name: string;
  url?: string;
  image?: string;
  email?: string;
  telephone?: string;
  jobTitle?: string;
}

/**
 * Organization Schema
 */
export interface Organization {
  '@type': 'Organization';
  name: string;
  url?: string;
  logo?: ImageObject | string;
  email?: string;
  telephone?: string;
  address?: PostalAddress;
}

export interface OrganizationInput {
  name: string;
  url?: string;
  logo?: string;
  email?: string;
  telephone?: string;
}

/**
 * ImageObject Schema
 */
export interface ImageObject {
  '@type': 'ImageObject';
  url: string;
  width?: number;
  height?: number;
  caption?: string;
}

/**
 * PostalAddress Schema
 */
export interface PostalAddress {
  '@type': 'PostalAddress';
  streetAddress?: string;
  addressLocality?: string;
  addressRegion?: string;
  postalCode?: string;
  addressCountry?: string;
}

/**
 * Article Schema
 */
export interface ArticleSchema extends BaseSchema {
  '@type': 'Article';
  headline: string;
  author: Person | Organization;
  datePublished?: string;
  dateModified?: string;
  description?: string;
  image?: ImageObject | ImageObject[];
  publisher?: Organization;
  articleBody?: string;
  url?: string;
  mainEntityOfPage?: string;
}

export interface ArticleInput {
  headline: string;
  authorName: string;
  authorUrl?: string;
  description?: string;
  datePublished?: string;
  dateModified?: string;
  image?: string | string[];
  articleBody?: string;
  url?: string;
  publisher?: {
    name: string;
    logo?: string;
    url?: string;
  };
}

/**
 * Product Schema
 */
export interface Product extends BaseSchema {
  '@type': 'Product';
  name: string;
  description?: string;
  image?: ImageObject | ImageObject[];
  brand?: Organization | string;
  offers?: Offer | Offer[];
  aggregateRating?: AggregateRating;
  review?: Review | Review[];
  sku?: string;
  mpn?: string;
  gtin?: string;
}

export interface ProductInput {
  name: string;
  description?: string;
  image?: string | string[];
  brand?: string;
  price?: string;
  priceCurrency?: string;
  availability?: string;
  url?: string;
  sku?: string;
  mpn?: string;
  gtin?: string;
  ratingValue?: number;
  reviewCount?: number;
}

/**
 * Offer Schema
 */
export interface Offer {
  '@type': 'Offer';
  price: string;
  priceCurrency: string;
  availability?: string;
  url?: string;
  priceValidUntil?: string;
  seller?: Organization;
}

/**
 * AggregateRating Schema
 */
export interface AggregateRating {
  '@type': 'AggregateRating';
  ratingValue: number;
  reviewCount: number;
  bestRating?: number;
  worstRating?: number;
}

/**
 * Review Schema
 */
export interface Review {
  '@type': 'Review';
  author: Person | Organization;
  datePublished?: string;
  reviewBody?: string;
  reviewRating?: Rating;
}

/**
 * Rating Schema
 */
export interface Rating {
  '@type': 'Rating';
  ratingValue: number;
  bestRating?: number;
  worstRating?: number;
}

/**
 * Recipe Schema
 */
export interface Recipe extends BaseSchema {
  '@type': 'Recipe';
  name: string;
  description?: string;
  image?: ImageObject | ImageObject[];
  author?: Person | Organization;
  datePublished?: string;
  prepTime?: string;
  cookTime?: string;
  totalTime?: string;
  recipeYield?: string;
  recipeCategory?: string;
  recipeCuisine?: string;
  recipeIngredient?: string[];
  recipeInstructions?: string | HowToStep[];
  nutrition?: NutritionInformation;
  aggregateRating?: AggregateRating;
}

export interface RecipeInput {
  name: string;
  description?: string;
  image?: string | string[];
  authorName?: string;
  prepTime?: string;
  cookTime?: string;
  recipeYield?: string;
  recipeCategory?: string;
  recipeCuisine?: string;
  ingredients?: string[];
  instructions?: string[];
}

/**
 * HowTo Schema
 */
export interface HowTo extends BaseSchema {
  '@type': 'HowTo';
  name: string;
  description?: string;
  image?: ImageObject | ImageObject[];
  totalTime?: string;
  estimatedCost?: MonetaryAmount;
  supply?: HowToSupply[];
  tool?: HowToTool[];
  step?: HowToStep[];
}

export interface HowToStep {
  '@type': 'HowToStep';
  name?: string;
  text: string;
  url?: string;
  image?: ImageObject;
}

export interface HowToSupply {
  '@type': 'HowToSupply';
  name: string;
}

export interface HowToTool {
  '@type': 'HowToTool';
  name: string;
}

export interface MonetaryAmount {
  '@type': 'MonetaryAmount';
  currency: string;
  value: string;
}

/**
 * NutritionInformation Schema
 */
export interface NutritionInformation {
  '@type': 'NutritionInformation';
  calories?: string;
  carbohydrateContent?: string;
  proteinContent?: string;
  fatContent?: string;
  fiberContent?: string;
  sugarContent?: string;
  sodiumContent?: string;
}

/**
 * FAQPage Schema
 */
export interface FAQPage extends BaseSchema {
  '@type': 'FAQPage';
  mainEntity: Question[];
}

export interface Question {
  '@type': 'Question';
  name: string;
  acceptedAnswer: Answer;
}

export interface Answer {
  '@type': 'Answer';
  text: string;
}

export interface FAQPageInput {
  questions: Array<{
    question: string;
    answer: string;
  }>;
}

/**
 * Event Schema
 */
export interface Event extends BaseSchema {
  '@type': 'Event';
  name: string;
  description?: string;
  startDate: string;
  endDate?: string;
  location?: Place | VirtualLocation;
  image?: ImageObject | ImageObject[];
  organizer?: Person | Organization;
  performer?: Person | Organization;
  offers?: Offer | Offer[];
}

export interface Place {
  '@type': 'Place';
  name: string;
  address: PostalAddress | string;
}

export interface VirtualLocation {
  '@type': 'VirtualLocation';
  url: string;
}

export interface EventInput {
  name: string;
  description?: string;
  startDate: string;
  endDate?: string;
  locationName?: string;
  locationAddress?: string;
  isVirtual?: boolean;
  virtualUrl?: string;
  image?: string | string[];
}

/**
 * Course Schema
 */
export interface Course extends BaseSchema {
  '@type': 'Course';
  name: string;
  description?: string;
  provider?: Organization;
  offers?: Offer | Offer[];
  aggregateRating?: AggregateRating;
}

export interface CourseInput {
  name: string;
  description?: string;
  providerName?: string;
  price?: string;
  priceCurrency?: string;
}

