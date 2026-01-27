import { NextRequest, NextResponse } from "next/server";
import { z } from "zod";
import { generateChatResponse } from "@/lib/gemini";

const conversationMessageSchema = z.object({
  role: z.enum(["user", "model"]),
  content: z.string(),
});

const requestSchema = z.object({
  message: z.string().min(1, "Message is required"),
  conversationHistory: z.array(conversationMessageSchema).optional().default([]),
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

    const { message, conversationHistory } = validation.data;

    const response = await generateChatResponse(
      message,
      conversationHistory || []
    );

    return NextResponse.json({
      success: true,
      response,
    });
  } catch (error) {
    console.error("[API] Chat error:", error);
    
    let errorMessage = "Failed to generate response";
    if (error instanceof Error) {
      if (error.message.includes("rate_limit")) {
        errorMessage = "Rate limit exceeded. Please try again in a moment.";
      } else if (error.message.includes("timeout")) {
        errorMessage = "Request timed out. Please try again.";
      } else {
        errorMessage = error.message;
      }
    }

    return NextResponse.json(
      {
        success: false,
        error: errorMessage,
      },
      { status: 500 }
    );
  }
}
