/**
 * Default filters for prompt refinement
 */
export interface DefaultFilters {
  answerFormat: "Paragraph" | "Bullet Points";
  toneOfResponse: "Formal" | "Informal" | "Neutral";
  outputDetail: number;
  audienceLevel: "General" | "Beginner" | "Intermediate" | "Expert";
  purpose: "Learning/Education" | "Professional/Work" | "Personal Interest" | "Research";
  includeVisuals: boolean;
  responseStructure: "Concise" | "Structured with Headings" | "Step-by-Step";
}

/**
 * Custom filter configuration
 */
export interface CustomFilter {
  type: "radio" | "checkbox" | "selectbox" | "text_input" | "slider";
  label: string;
  key: string;
  options?: Array<string | { label: string; value: string }>;
  min?: number; // For slider
  max?: number; // For slider
  step?: number; // For slider
}

/**
 * Response from custom filters generation API
 */
export interface CustomFiltersResponse {
  custom_filters: CustomFilter[];
}

/**
 * Chat message structure
 */
export interface ChatMessage {
  id: string;
  role: "user" | "model";
  content: string;
  timestamp: Date;
}

/**
 * File upload result
 */
export interface FileUploadResult {
  filename: string;
  url: string;
  text?: string;
  type: string;
}

/**
 * Request for prompt refinement
 */
export interface RefinementRequest {
  originalPrompt: string;
  defaultFilters: DefaultFilters;
  customFilters: Record<string, string | boolean | number>;
  fileContents?: string[];
}

/**
 * Request for generating custom filters
 */
export interface GenerateFiltersRequest {
  prompt: string;
  fileContents?: string[];
}
