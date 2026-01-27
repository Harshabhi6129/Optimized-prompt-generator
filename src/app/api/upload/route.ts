import { NextRequest, NextResponse } from "next/server";
import { processMultipleFiles, combineExtractedText } from "@/lib/file-processor";

export const config = {
  api: {
    bodyParser: false,
  },
};

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const files = formData.getAll("files") as File[];

    if (!files || files.length === 0) {
      return NextResponse.json(
        {
          success: false,
          error: "No files provided",
        },
        { status: 400 }
      );
    }

    console.log(`[API] Processing ${files.length} uploaded files`);

    const processedFiles = await processMultipleFiles(files);
    const combinedText = combineExtractedText(processedFiles);

    const successCount = processedFiles.filter((f) => f.success).length;
    console.log(`[API] Upload complete: ${successCount}/${files.length} successful`);

    return NextResponse.json({
      success: true,
      files: processedFiles,
      combinedText,
    });
  } catch (error) {
    console.error("[API] Upload error:", error);
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : "Failed to process files",
      },
      { status: 500 }
    );
  }
}
