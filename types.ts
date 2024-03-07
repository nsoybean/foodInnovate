export interface Pokedex {
  searchString: string;
  rank: null;
  searchPageUrl: null;
  searchPageLoadedUrl: null;
  isAdvertisement: boolean;
  title: string;
  subTitle: null;
  description: null;
  price: string;
  categoryName: string;
  address: string;
  neighborhood: string;
  street: string;
  city: string;
  postalCode: string;
  state: null;
  countryCode: string;
  website: string;
  phone: string;
  phoneUnformatted: string;
  claimThisBusiness: boolean;
  location: Location;
  locatedIn: string;
  plusCode: string;
  menu: null;
  totalScore: number;
  permanentlyClosed: boolean;
  temporarilyClosed: boolean;
  placeId: string;
  categories: string[];
  cid: string;
  reviewsCount: number;
  reviewsDistribution: ReviewsDistribution;
  imagesCount: number;
  imageCategories: string[];
  scrapedAt: Date;
  reserveTableUrl: null;
  googleFoodUrl: string;
  hotelStars: null;
  hotelDescription: null;
  checkInDate: null;
  checkOutDate: null;
  similarHotelsNearby: null;
  hotelReviewSummary: null;
  hotelAds: any[];
  popularTimesLiveText: string;
  popularTimesLivePercent: number;
  popularTimesHistogram: PopularTimesHistogram;
  openingHours: OpeningHour[];
  peopleAlsoSearch: PeopleAlsoSearch[];
  placesTags: any[];
  reviewsTags: ReviewsTag[];
  additionalInfo: AdditionalInfo;
  gasPrices: any[];
  questionsAndAnswers: null;
  updatesFromCustomers: null;
  url: string;
  webResults: any[];
  orderBy: OrderBy[];
  imageUrls: any[];
  name: string;
  text: string;
  textTranslated: null;
  publishAt: string;
  publishedAtDate: Date;
  likesCount: number;
  reviewId: string;
  reviewUrl: string;
  reviewerId: string;
  reviewerUrl: string;
  reviewerPhotoUrl: string;
  reviewerNumberOfReviews: number;
  isLocalGuide: boolean;
  reviewOrigin: string;
  stars: number;
  rating: null;
  responseFromOwnerDate: null;
  responseFromOwnerText: null;
  reviewImageUrls: any[];
  reviewContext: ReviewContext;
  reviewDetailedRating: ReviewDetailedRating;
}

export interface AdditionalInfo {
  "Service options": ServiceOption[];
  Accessibility: Accessibility[];
  Offerings: Offering[];
  "Dining options": DiningOption[];
  Atmosphere: Atmosphere[];
  Crowd: Crowd[];
  Planning: Planning[];
  Payments: Payment[];
  Children: Child[];
}

export interface Accessibility {
  "Wheelchair-accessible entrance": boolean;
}

export interface Atmosphere {
  Casual: boolean;
}

export interface Child {
  "Good for kids": boolean;
}

export interface Crowd {
  Groups: boolean;
}

export interface DiningOption {
  Breakfast?: boolean;
  Brunch?: boolean;
  Lunch?: boolean;
  Dinner?: boolean;
}

export interface Offering {
  Coffee?: boolean;
  "Small plates"?: boolean;
}

export interface Payment {
  "Credit cards"?: boolean;
  "Debit cards"?: boolean;
  "NFC mobile payments"?: boolean;
}

export interface Planning {
  "Accepts reservations": boolean;
}

export interface ServiceOption {
  Delivery?: boolean;
  Takeout?: boolean;
  "Dine-in"?: boolean;
}

export interface Location {
  lat: number;
  lng: number;
}

export interface OpeningHour {
  day: string;
  hours: string;
}

export interface OrderBy {
  name: string;
  url: string;
  orderUrl: string;
}

export interface PeopleAlsoSearch {
  category: string;
  title: string;
  reviewsCount: number;
  totalScore: number;
}

export interface PopularTimesHistogram {
  Su: Fr[];
  Mo: Fr[];
  Tu: Fr[];
  We: Fr[];
  Th: Fr[];
  Fr: Fr[];
  Sa: Fr[];
}

export interface Fr {
  hour: number;
  occupancyPercent: number;
}

export interface ReviewContext {
  Service: string;
  "Meal type": string;
  "Price per person": string;
}

export interface ReviewDetailedRating {
  Food: number;
  Service: number;
  Atmosphere: number;
}

export interface ReviewsDistribution {
  oneStar: number;
  twoStar: number;
  threeStar: number;
  fourStar: number;
  fiveStar: number;
}

export interface ReviewsTag {
  title: string;
  count: number;
}
