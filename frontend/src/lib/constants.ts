export const CATEGORIES = [
  "All businesses",
  "Hospitals",
  "Clinics",
  "Hotels",
  "Restaurants",
  "Schools",
  "Colleges",
  "Real estate agencies",
  "Textile companies",
  "Manufacturers",
  "Travel agencies",
  "Construction companies",
  "Digital agencies",
  "Local shops",
];

export const DEFAULT_FILTERS = {
  country: "India",
  state: "Tamil Nadu",
  city: "",
  category: "All businesses",
  industry: "",
  website_available: true,
  limit: 50,
};

export const PRIORITY_COLOR: Record<string, string> = {
  high: "text-red-600 bg-red-50 border-red-100",
  medium: "text-orange-600 bg-orange-50 border-orange-100",
  low: "text-green-600 bg-green-50 border-green-100",
};

export const STATUS_COLOR: Record<string, string> = {
  new: "text-blue-600 bg-blue-50 border-blue-100",
  contacted: "text-purple-600 bg-purple-50 border-purple-100",
  interested: "text-indigo-600 bg-indigo-50 border-indigo-100",
  converted: "text-green-600 bg-green-50 border-green-100",
};

export const STATUS_LABELS: Record<string, string> = {
  new: "New",
  contacted: "Contacted",
  interested: "Interested",
  converted: "Converted",
};

export const SCORE_LABEL = (score: number) => {
  if (score >= 70) return "High Priority";
  if (score >= 40) return "Medium Priority";
  return "Low Priority";
};
