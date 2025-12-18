
export interface NutritionalInfo {
  calories: string;
  protein: string;
  fat: string;
  carbs: string;
  sugar?: string;
  fiber?: string;
  sodium?: string;
}

export interface ProductAnalysis {
  productName: string;
  brand: string;
  isSafeForConsumption: boolean;
  safetyReasoning: string;
  nutritionalInfo: NutritionalInfo;
  expirationInfo: string;
  allergens: string[];
}

export type AppState = 'IDLE' | 'CAPTURING' | 'ANALYZING' | 'RESULT' | 'ERROR';
