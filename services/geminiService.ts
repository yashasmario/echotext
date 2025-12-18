import { GoogleGenAI } from "@google/genai";
import { ANALYSIS_SYSTEM_INSTRUCTION, GEMINI_MODEL, RESPONSE_SCHEMA } from "../constants";
import { ProductAnalysis } from "../types";

const api_key = import.meta.env.VITE_API_KEY;

export const analyzeProductImage = async (base64Image: string): Promise<ProductAnalysis> => {
  const ai = new GoogleGenAI({ apiKey: api_key });
  
  // Strip the prefix if present
  const base64Data = base64Image.replace(/^data:image\/(png|jpeg|webp);base64,/, '');

  try {
    const response = await ai.models.generateContent({
      model: GEMINI_MODEL,
      contents: {
        parts: [
          {
            inlineData: {
              mimeType: 'image/jpeg',
              data: base64Data,
            },
          },
          {
            text: "Analyze this food product. Identify it, check safety/expiration, and get nutritional macros. If it's a barcode, identify the product it represents.",
          },
        ],
      },
      config: {
        systemInstruction: ANALYSIS_SYSTEM_INSTRUCTION,
        responseMimeType: "application/json",
        responseSchema: RESPONSE_SCHEMA,
      },
    });

    const resultText = response.text;
    if (!resultText) {
      throw new Error("No response text from Gemini");
    }

    return JSON.parse(resultText) as ProductAnalysis;
  } catch (error) {
    console.error("Gemini Analysis Error:", error);
    throw error;
  }
};
