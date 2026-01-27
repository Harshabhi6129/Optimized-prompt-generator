"use client";

import { useState, useRef } from "react";
import { Upload, X, ImageIcon, FileText, File } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { truncateText } from "@/lib/utils";

interface UploadedFile {
  name: string;
  type: string;
  text: string;
  success: boolean;
  error?: string;
}

interface FileUploadProps {
  onFilesProcessed: (extractedText: string) => void;
}

export function FileUpload({ onFilesProcessed }: FileUploadProps) {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const getFileIcon = (type: string) => {
    if (type.startsWith("image/")) return ImageIcon;
    if (type === "application/pdf" || type.includes("document")) return FileText;
    return File;
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = e.target.files;
    if (!selectedFiles || selectedFiles.length === 0) return;

    setIsUploading(true);

    try {
      const formData = new FormData();
      Array.from(selectedFiles).forEach((file) => {
        formData.append("files", file);
      });

      const response = await fetch("/api/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Upload failed");
      }

      const data = await response.json();
      
      if (data.success) {
        setFiles((prev) => [...prev, ...data.files]);
        onFilesProcessed(data.combinedText);
      } else {
        alert("Failed to process files");
      }
    } catch (error) {
      console.error("Upload error:", error);
      alert("Failed to upload files. Please try again.");
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  const removeFile = (index: number) => {
    const updatedFiles = files.filter((_, i) => i !== index);
    setFiles(updatedFiles);

    const successfulFiles = updatedFiles.filter((f) => f.success && f.text);
    const combinedText = successfulFiles.length > 0
      ? `--- Extracted Content from Uploaded Files ---\n\n${successfulFiles
          .map((f) => `[From ${f.name}]\n${f.text}`)
          .join("\n\n")}`
      : "";

    onFilesProcessed(combinedText);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>📤 Upload Files</CardTitle>
        <CardDescription>
          Supported formats: PNG, JPG, PDF, DOCX, TXT
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".png,.jpg,.jpeg,.pdf,.docx,.txt,image/*,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain"
          onChange={handleFileChange}
          className="hidden"
        />
        
        <Button
          onClick={() => fileInputRef.current?.click()}
          disabled={isUploading}
          className="w-full"
        >
          <Upload className="w-4 h-4 mr-2" />
          {isUploading ? "Processing..." : "Choose Files"}
        </Button>

        {files.length > 0 && (
          <div className="space-y-2 max-h-60 overflow-y-auto rounded-md bg-secondary/50 p-3">
            {files.map((file, index) => {
              const Icon = getFileIcon(file.type);
              return (
                <div
                  key={index}
                  className="flex items-center justify-between gap-2 rounded-md bg-background p-3 hover:bg-accent transition-colors"
                >
                  <div className="flex items-center gap-3 flex-1 min-w-0">
                    <Icon className="w-5 h-5 flex-shrink-0 text-muted-foreground" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">
                        {truncateText(file.name, 30)}
                      </p>
                      {file.success ? (
                        <p className="text-xs text-muted-foreground">
                          {file.text.length} characters
                        </p>
                      ) : (
                        <p className="text-xs text-destructive">
                          {file.error || "Processing failed"}
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <Badge variant="secondary" className="text-xs">
                      {file.type.split("/")[1] || "file"}
                    </Badge>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => removeFile(index)}
                      className="h-8 w-8"
                    >
                      <X className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
