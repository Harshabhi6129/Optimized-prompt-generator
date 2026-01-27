import { createWorker } from "tesseract.js";

const pdfParse = require("pdf-parse");
const mammoth = require("mammoth");

export interface ProcessedFile {
  filename: string;
  type: string;
  text: string;
  success: boolean;
  error?: string;
}

/**
 * Process image file using Tesseract OCR
 */
export async function processImage(
  buffer: Buffer,
  filename: string
): Promise<ProcessedFile> {
  let worker;
  try {
    console.log(`[OCR] Processing image: ${filename}`);
    worker = await createWorker("eng");
    const { data } = await worker.recognize(buffer);
    await worker.terminate();
    
    console.log(`[OCR] Successfully extracted ${data.text.length} characters`);
    return {
      filename,
      type: "image",
      text: data.text.trim(),
      success: true,
    };
  } catch (error) {
    if (worker) await worker.terminate();
    console.error(`[OCR] Error processing ${filename}:`, error);
    return {
      filename,
      type: "image",
      text: "",
      success: false,
      error: error instanceof Error ? error.message : "OCR processing failed",
    };
  }
}

/**
 * Process PDF file using pdf-parse
 */
export async function processPDF(
  buffer: Buffer,
  filename: string
): Promise<ProcessedFile> {
  try {
    console.log(`[PDF] Processing: ${filename}`);
    const data = await pdfParse(buffer);
    
    console.log(`[PDF] Extracted ${data.text.length} characters from ${data.numpages} pages`);
    return {
      filename,
      type: "pdf",
      text: data.text.trim(),
      success: true,
    };
  } catch (error) {
    console.error(`[PDF] Error processing ${filename}:`, error);
    return {
      filename,
      type: "pdf",
      text: "",
      success: false,
      error: error instanceof Error ? error.message : "PDF processing failed",
    };
  }
}

/**
 * Process DOCX file using mammoth
 */
export async function processDOCX(
  buffer: Buffer,
  filename: string
): Promise<ProcessedFile> {
  try {
    console.log(`[DOCX] Processing: ${filename}`);
    const result = await mammoth.extractRawText({ buffer });
    
    console.log(`[DOCX] Extracted ${result.value.length} characters`);
    return {
      filename,
      type: "docx",
      text: result.value.trim(),
      success: true,
    };
  } catch (error) {
    console.error(`[DOCX] Error processing ${filename}:`, error);
    return {
      filename,
      type: "docx",
      text: "",
      success: false,
      error: error instanceof Error ? error.message : "DOCX processing failed",
    };
  }
}

/**
 * Process plain text file
 */
export async function processText(
  buffer: Buffer,
  filename: string
): Promise<ProcessedFile> {
  try {
    console.log(`[TEXT] Processing: ${filename}`);
    const text = buffer.toString("utf-8").trim();
    
    console.log(`[TEXT] Extracted ${text.length} characters`);
    return {
      filename,
      type: "text",
      text,
      success: true,
    };
  } catch (error) {
    console.error(`[TEXT] Error processing ${filename}:`, error);
    return {
      filename,
      type: "text",
      text: "",
      success: false,
      error: error instanceof Error ? error.message : "Text processing failed",
    };
  }
}

/**
 * Process a single file based on its MIME type
 */
export async function processFile(file: File): Promise<ProcessedFile> {
  try {
    const buffer = Buffer.from(await file.arrayBuffer());
    
    if (buffer.length === 0) {
      return {
        filename: file.name,
        type: file.type,
        text: "",
        success: false,
        error: "File is empty",
      };
    }

    if (file.type.startsWith("image/")) {
      return await processImage(buffer, file.name);
    }

    if (file.type === "application/pdf") {
      return await processPDF(buffer, file.name);
    }

    if (
      file.type ===
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ) {
      return await processDOCX(buffer, file.name);
    }

    if (file.type === "text/plain") {
      return await processText(buffer, file.name);
    }

    return {
      filename: file.name,
      type: file.type,
      text: "",
      success: false,
      error: `Unsupported file type: ${file.type}`,
    };
  } catch (error) {
    console.error(`[FILE] Error processing ${file.name}:`, error);
    return {
      filename: file.name,
      type: file.type,
      text: "",
      success: false,
      error: error instanceof Error ? error.message : "File processing failed",
    };
  }
}

/**
 * Process multiple files in parallel
 */
export async function processMultipleFiles(
  files: File[]
): Promise<ProcessedFile[]> {
  console.log(`[BATCH] Processing ${files.length} files`);
  const results = await Promise.all(files.map((file) => processFile(file)));
  
  const successful = results.filter((r) => r.success).length;
  console.log(`[BATCH] Completed: ${successful}/${files.length} successful`);
  
  return results;
}

/**
 * Combine extracted text from multiple processed files
 */
export function combineExtractedText(processedFiles: ProcessedFile[]): string {
  const successfulFiles = processedFiles.filter((f) => f.success && f.text);

  if (successfulFiles.length === 0) {
    return "";
  }

  const parts = ["--- Extracted Content from Uploaded Files ---\n"];

  successfulFiles.forEach((file) => {
    parts.push(`[From ${file.filename}]`);
    parts.push(file.text);
    parts.push("");
  });

  return parts.join("\n");
}
