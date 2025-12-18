
import { Type } from "@google/genai";

export const GEMINI_MODEL = 'gemini-3-flash-preview';

export const ANALYSIS_SYSTEM_INSTRUCTION = `
You are a specialized assistant for visually impaired users. 
Your task is to analyze images of food products (packaging, labels, or barcodes).
Identify the product accurately. 
Evaluate safety: Look for expiration dates, signs of spoilage, or recalls if identifiable. 
Extract nutritional facts focusing on macros (Calories, Protein, Fat, Carbs).
Identify common allergens.

Return the data in a clear, structured JSON format. 
Be honest: if you cannot read a label clearly, indicate that in the reasoning.
`;

export const RESPONSE_SCHEMA = {
  type: Type.OBJECT,
  properties: {
    productName: { type: Type.STRING, description: "Name of the food product" },
    brand: { type: Type.STRING, description: "Brand of the product" },
    isSafeForConsumption: { type: Type.BOOLEAN, description: "Whether the item appears safe to eat" },
    safetyReasoning: { type: Type.STRING, description: "Explanation of safety assessment" },
    nutritionalInfo: {
      type: Type.OBJECT,
      properties: {
        calories: { type: Type.STRING },
        protein: { type: Type.STRING },
        fat: { type: Type.STRING },
        carbs: { type: Type.STRING },
        sugar: { type: Type.STRING },
        fiber: { type: Type.STRING },
        sodium: { type: Type.STRING }
      },
      required: ["calories", "protein", "fat", "carbs"]
    },
    expirationInfo: { type: Type.STRING, description: "Found expiration or best by date" },
    allergens: { 
      type: Type.ARRAY, 
      items: { type: Type.STRING },
      description: "List of identified allergens"
    }
  },
  required: ["productName", "brand", "isSafeForConsumption", "safetyReasoning", "nutritionalInfo", "allergens"]
};
