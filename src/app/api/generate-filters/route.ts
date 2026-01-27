import { NextRequest, NextResponse } from "next/server";
import { z } from "zod";
import { generateCustomFilters } from "@/lib/gemini";

const requestSchema = z.object({
  naivePrompt: z.string().min(1, "Prompt is required"),
  extractedText: z.string().optional().default(""),
});

export async function POST(request: NextRequest) {
  try {
    console.log("[API] /api/generate-filters called");
    
    const body = await request.json();
    console.log("[API] Request body:", body);
    
    const validation = requestSchema.safeParse(body);

    if (!validation.success) {
      console.error("[API] Validation failed:", validation.error.issues);
      return NextResponse.json(
        {
          success: false,
          error: "Validation failed",
          details: validation.error.issues,
        },
        { status: 400 }
      );
    }

    const { naivePrompt, extractedText } = validation.data;
    console.log("[API] Validated prompt:", naivePrompt);
    console.log("[API] Extracted text length:", extractedText?.length || 0);

    const combinedPrompt = extractedText
      ? `${naivePrompt}

${extractedText}`
      : naivePrompt;

    console.log("[API] Combined prompt:", combinedPrompt);
    console.log("[API] Calling generateCustomFilters...");
    
    const result = await generateCustomFilters(combinedPrompt);
    
    console.log("[API] Filters generated successfully:", result);
    console.log("[API] Number of filters:", result.custom_filters?.length || 0);

    return NextResponse.json({
      success: true,
      filters: result,
    });
  } catch (error) {
    console.error("[API] Generate filters error:", error);
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : "Failed to generate filters",
      },
      { status: 500 }
    );
  }
}
