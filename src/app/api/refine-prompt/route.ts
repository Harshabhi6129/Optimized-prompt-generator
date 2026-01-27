import { NextRequest, NextResponse } from "next/server";
import { z } from "zod";
import { refinePromptWithGemini } from "@/lib/gemini";
import { buildFiltersText } from "@/lib/utils";

const defaultFiltersSchema = z.object({
  answerFormat: z.enum(["Paragraph", "Bullet Points"]),
  toneOfResponse: z.enum(["Formal", "Informal", "Neutral"]),
  outputDetail: z.number().min(1).max(5),
  audienceLevel: z.enum(["General", "Beginner", "Intermediate", "Expert"]),
  purpose: z.enum([
    "Learning/Education",
    "Professional/Work",
    "Personal Interest",
    "Research",
  ]),
  includeVisuals: z.boolean(),
  responseStructure: z.enum([
    "Concise",
    "Structured with Headings",
    "Step-by-Step",
  ]),
});

const requestSchema = z.object({
  naivePrompt: z.string().min(1, "Prompt is required"),
  defaultFilters: defaultFiltersSchema,
  customFilters: z.record(z.string(), z.union([z.string(), z.boolean(), z.number()])).optional().default({}),
  extractedText: z.string().optional().default(""),
});

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const validation = requestSchema.safeParse(body);

    if (!validation.success) {
      return NextResponse.json(
        {
          success: false,
          error: "Validation failed",
          details: validation.error.issues,
        },
        { status: 400 }
      );
    }

    const { naivePrompt, defaultFilters, customFilters, extractedText } =
      validation.data;

    const filtersText = buildFiltersText(
      defaultFilters,
      customFilters as Record<string, string | boolean | number>
    );

    const combinedPrompt = extractedText
      ? `${naivePrompt}\n\n${extractedText}`
      : naivePrompt;

    const refinedPrompt = await refinePromptWithGemini(
      combinedPrompt,
      filtersText
    );

    return NextResponse.json({
      success: true,
      refinedPrompt,
    });
  } catch (error) {
    console.error("[API] Refine prompt error:", error);
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : "Failed to refine prompt",
      },
      { status: 500 }
    );
  }
}
