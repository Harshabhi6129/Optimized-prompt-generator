import { GoogleGenerativeAI } from "@google/generative-ai";
import { CustomFiltersResponse } from "@/types";

const apiKey = process.env.GOOGLE_GEMINI_API_KEY;

if (!apiKey) {
  console.error("[FATAL] GOOGLE_GEMINI_API_KEY is not set!");
  console.error("[FATAL] Available env vars:", Object.keys(process.env).filter(k => k.includes('GEMINI')));
  throw new Error("GOOGLE_GEMINI_API_KEY is not set in environment variables");
}

console.log("[INIT] Gemini API initialized");
console.log("[INIT] API Key loaded (first 10 chars):", apiKey.substring(0, 10));

const genAI = new GoogleGenerativeAI(apiKey);

const FALLBACK_FILTERS: CustomFiltersResponse = {
  custom_filters: [
    {
      type: "radio",
      label: "What is your primary goal?",
      key: "primary_goal",
      options: ["Create something new", "Improve existing work", "Learn and understand", "Solve a problem"]
    },
    {
      type: "checkbox",
      label: "What aspects are most important?",
      key: "important_aspects",
      options: ["Quality", "Speed", "Innovation", "Simplicity", "Completeness"]
    },
    {
      type: "selectbox",
      label: "Project timeline?",
      key: "timeline",
      options: ["Urgent (within days)", "Soon (within weeks)", "Flexible (within months)", "Long-term (no deadline)"]
    },
    {
      type: "text_input",
      label: "Describe any additional requirements:",
      key: "custom_free_text",
    },
  ],
};


/**
 * Generate custom filters based on user's naive prompt
 */
export async function generateCustomFilters(
  naivePrompt: string
): Promise<CustomFiltersResponse> {
  console.log("=================================================");
  console.log("[DEBUG] generateCustomFilters called");
  console.log("[DEBUG] Input prompt:", naivePrompt);
  console.log("[DEBUG] API Key exists:", !!process.env.GOOGLE_GEMINI_API_KEY);
  console.log("[DEBUG] API Key first 10 chars:", process.env.GOOGLE_GEMINI_API_KEY?.substring(0, 10));
  console.log("=================================================");

  const systemInstruction = `You are an Expert AI Consultant. Your goal is to deeply understand the user's intent and identify CRITICAL MISSING INFORMATION needed to provide the perfect solution.

  Analyze the user's "Naive Prompt" and any "Extracted Text". 
  
  **Your Task:**
  1. Identify ambiguities, missing constraints, or context gaps.
  2. Generate 4-7 specific, high-value questions (filters) to close these gaps.
  3. Use a mix of UI elements:
     - **radio**: For single choices (e.g., "Tone?").
     - **checkbox**: For multiple features/options.
     - **slider**: For numeric ranges or scales (e.g., "Word Count", "Creativity Level", "Budget").
     - **selectbox**: For long lists of options.
     - **text_input**: ALWAYS end with this for "Any other details?".
  
  **Rules:**
  - DO NOT ask generic questions if the answer is already in the prompt/files.
  - Be specific to the domain (coding, writing, business, etc.).
  - For Sliders: Set reasonable min, max, and step values.
  
  **Example JSON Output:**
  {
    "custom_filters": [
      {
        "type": "radio",
        "label": "Who is the target audience?",
        "key": "audience",
        "options": ["Developers", "Managers", "End Users"]
      },
      {
        "type": "slider",
        "label": "How detailed should the explanation be? (1=Brief, 10=Deep Dive)",
        "key": "depth",
        "min": 1,
        "max": 10,
        "step": 1
      },
      {
        "type": "text_input",
        "label": "Any specific technologies or constraints?",
        "key": "constraints"
      }
    ]
  }
  
  Return ONLY valid JSON.`;

  const model = genAI.getGenerativeModel({
    model: "gemini-pro",
    generationConfig: {
      temperature: 0.9,
      maxOutputTokens: 2048,
    },
  });

  console.log("[DEBUG] Model created successfully");

  const maxRetries = 3;
  const fullPrompt = `${systemInstruction}

"${naivePrompt}"`;

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      console.log(`[DEBUG] Attempt ${attempt + 1}: Calling Gemini API...`);
      console.log(`[DEBUG] Full prompt being sent:`, fullPrompt.substring(0, 300) + '...');

      const result = await model.generateContent(fullPrompt);

      console.log(`[DEBUG] Attempt ${attempt + 1}: API call successful`);

      const response = await result.response;
      let text = response.text().trim();

      console.log(`[DEBUG] Attempt ${attempt + 1}: Raw response length:`, text.length);
      console.log(`[DEBUG] Attempt ${attempt + 1}: First 500 chars:`, text.substring(0, 500));
      console.log(`[DEBUG] Attempt ${attempt + 1}: Last 200 chars:`, text.substring(text.length - 200));

      // Remove markdown code blocks if present
      text = text.replace(/```json\s*/g, "").replace(/```\s*/g, "");

      // Extract JSON if wrapped in other text
      const jsonMatch = text.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        console.log(`[DEBUG] Attempt ${attempt + 1}: JSON extracted from response`);
        text = jsonMatch[0];
      }

      console.log(`[DEBUG] Attempt ${attempt + 1}: Cleaned text for parsing:`, text);

      const parsed = JSON.parse(text);

      console.log(`[DEBUG] Attempt ${attempt + 1}: JSON parsed successfully`);
      console.log(`[DEBUG] Attempt ${attempt + 1}: Parsed object:`, JSON.stringify(parsed, null, 2));

      // Validate structure
      if (!parsed.custom_filters || !Array.isArray(parsed.custom_filters)) {
        throw new Error("Invalid response structure: missing custom_filters array");
      }

      console.log(`[DEBUG] Attempt ${attempt + 1}: Found ${parsed.custom_filters.length} filters`);

      // Validate each filter
      for (const filter of parsed.custom_filters) {
        if (!filter.type || !filter.label || !filter.key) {
          throw new Error("Filter missing required fields: type, label, or key");
        }
      }

      console.log(`[DEBUG] Attempt ${attempt + 1}: All filters validated successfully`);
      console.log(`[DEBUG] SUCCESS: Returning ${parsed.custom_filters.length} custom filters`);
      return parsed;

    } catch (error) {
      console.error(`[DEBUG] Attempt ${attempt + 1}: FAILED`);
      console.error(`[DEBUG] Error type:`, (error as any)?.constructor?.name || 'Unknown');
      console.error(`[DEBUG] Error message:`, error instanceof Error ? error.message : 'Unknown error');
      console.error(`[DEBUG] Full error:`, error);

      if (attempt === maxRetries - 1) {
        console.error("[DEBUG] ALL RETRIES FAILED - RETURNING FALLBACK FILTERS");
        console.error("[DEBUG] This means Gemini API is not working or returning invalid data");
        return {
          custom_filters: [
            {
              type: "radio",
              label: "What is your primary goal?",
              key: "primary_goal",
              options: ["Create something new", "Improve existing work", "Learn and understand", "Solve a problem"]
            },
            {
              type: "checkbox",
              label: "What aspects are most important?",
              key: "important_aspects",
              options: ["Quality", "Speed", "Innovation", "Simplicity", "Completeness"]
            },
            {
              type: "selectbox",
              label: "Project timeline?",
              key: "timeline",
              options: ["Urgent (within days)", "Soon (within weeks)", "Flexible (within months)", "Long-term (no deadline)"]
            },
            {
              type: "text_input",
              label: "Describe any additional requirements:",
              key: "custom_free_text",
            },
          ],
        };
      }

      await new Promise(resolve => setTimeout(resolve, 1000 * (attempt + 1)));
    }
  }

  return FALLBACK_FILTERS;
}

/**
 * Refine prompt with Gemini based on filters
 */
export async function refinePromptWithGemini(
  naivePrompt: string,
  filtersText: string
): Promise<string> {
  const model = genAI.getGenerativeModel({
    model: "gemini-pro",
    systemInstruction: `You are an expert prompt optimizer. Your task is to refine user prompts.

RULES:
- Output ONLY the refined prompt (no explanations, no meta-commentary)
- Incorporate all details from the naive prompt
- Seamlessly integrate user preferences from the filters
- Make the prompt clear, comprehensive, and precise
- Preserve the original intent
- Do not add markdown formatting`,
  });

  try {
    console.log("[Gemini] Refining prompt with filters");

    const result = await model.generateContent(
      `Refine this prompt based on the user preferences:\n\nOriginal Prompt:\n${naivePrompt}\n\nUser Preferences:\n${filtersText}\n\nProvide the refined prompt:`
    );

    const refined = result.response.text().trim();
    console.log("[Gemini] Prompt refined successfully");

    return refined;

  } catch (error) {
    console.error("[Gemini] Error refining prompt:", error);
    throw new Error(
      `Failed to refine prompt: ${error instanceof Error ? error.message : "Unknown error"}`
    );
  }
}

/**
 * Generate chat response using Gemini 1.5 Flash
 * Replaces OpenAI GPT for chat functionality
 */
export async function generateChatResponse(
  userMessage: string,
  conversationHistory: Array<{ role: "user" | "model"; content: string }> = []
): Promise<string> {
  const model = genAI.getGenerativeModel({
    model: "gemini-pro",
    generationConfig: {
      temperature: 0.7,
      maxOutputTokens: 2048,
    },
  });

  try {
    // Build conversation history for Gemini
    const chatHistory = conversationHistory.map(msg => ({
      role: msg.role === "user" ? "user" : "model",
      parts: [{ text: msg.content }],
    }));

    // Start chat with history
    const chat = model.startChat({
      history: chatHistory,
      generationConfig: {
        temperature: 0.7,
        maxOutputTokens: 2048,
      },
    });

    // Send message
    const result = await chat.sendMessage(userMessage);
    const response = await result.response;
    const text = response.text().trim();

    console.log(`[Gemini Chat] Response length: ${text.length} characters`);
    return text;
  } catch (error) {
    console.error("[Gemini Chat] Error:", error);
    throw new Error("Failed to generate chat response with Gemini AI");
  }
}

/**
 * Test function to verify Gemini API is working
 * Call this from the browser console to debug
 */
export async function testGeminiConnection() {
  try {
    console.log("[TEST] Testing Gemini API connection...");
    const model = genAI.getGenerativeModel({ model: "gemini-pro" });
    const result = await model.generateContent("Say 'Hello, API is working!'");
    const response = await result.response;
    const text = response.text();
    console.log("[TEST] Success! Response:", text);
    return text;
  } catch (error) {
    console.error("[TEST] Failed!", error);
    return null;
  }
}

/**
 * List available Gemini models for debugging
 */
export async function listAvailableModels() {
  try {
    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models?key=${process.env.GOOGLE_GEMINI_API_KEY}`
    );
    const data = await response.json();
    console.log("Available models:", data.models?.map((m: any) => m.name));
    return data;
  } catch (error) {
    console.error("Error listing models:", error);
  }
}
