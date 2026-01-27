"use client";

import { useState } from "react";
import { Sparkles, Wand2, CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { FileUpload } from "@/components/file-upload";
import { FilterPanel } from "@/components/filter-panel";
import { ChatInterface } from "@/components/chat-interface";
import { DefaultFilters, CustomFilter } from "@/types";

export function PromptRefinementApp() {
  const [naivePrompt, setNaivePrompt] = useState("");
  const [extractedText, setExtractedText] = useState("");

  const [defaultFilters, setDefaultFilters] = useState<DefaultFilters>({
    answerFormat: "Paragraph",
    toneOfResponse: "Neutral",
    outputDetail: 3,
    audienceLevel: "General",
    purpose: "Learning/Education",
    includeVisuals: false,
    responseStructure: "Concise",
  });
  const [customFilters, setCustomFilters] = useState<CustomFilter[]>([]);
  const [customFilterValues, setCustomFilterValues] = useState<Record<string, any>>({});

  const [refinedPrompt, setRefinedPrompt] = useState("");

  const [isGeneratingFilters, setIsGeneratingFilters] = useState(false);
  const [isRefining, setIsRefining] = useState(false);
  const [filtersGenerated, setFiltersGenerated] = useState(false);
  const [promptRefined, setPromptRefined] = useState(false);

  const handleGenerateFilters = async () => {
    if (!naivePrompt.trim()) {
      alert("Please enter a prompt first");
      return;
    }

    setIsGeneratingFilters(true);
    setFiltersGenerated(false);

    try {
      const response = await fetch("/api/generate-filters", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          naivePrompt,
          extractedText,
        }),
      });

      const data = await response.json();

      if (data.success) {
        setCustomFilters(data.filters.custom_filters || []);
        const initialValues: Record<string, any> = {};
        data.filters.custom_filters?.forEach((filter: CustomFilter) => {
          if (filter.type === "checkbox" && filter.options) {
            initialValues[filter.key] = [];
          } else if (filter.type === "text_input") {
            initialValues[filter.key] = "";
          } else {
            initialValues[filter.key] = "";
          }
        });
        setCustomFilterValues(initialValues);
        setFiltersGenerated(true);
      } else {
        alert("Failed to generate filters: " + (data.error || "Unknown error"));
      }
    } catch (error) {
      console.error("Error generating filters:", error);
      alert("Failed to generate filters. Please try again.");
    } finally {
      setIsGeneratingFilters(false);
    }
  };

  const handleRefinePrompt = async (withFilters: boolean) => {
    if (!naivePrompt.trim()) {
      alert("Please enter a prompt first");
      return;
    }

    setIsRefining(true);
    setPromptRefined(false);

    try {
      const response = await fetch("/api/refine-prompt", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          naivePrompt,
          defaultFilters: withFilters ? defaultFilters : {
            answerFormat: "Paragraph",
            toneOfResponse: "Neutral",
            outputDetail: 3,
            audienceLevel: "General",
            purpose: "Learning/Education",
            includeVisuals: false,
            responseStructure: "Concise",
          },
          customFilters: withFilters ? customFilterValues : {},
          extractedText,
        }),
      });

      const data = await response.json();

      if (data.success) {
        setRefinedPrompt(data.refinedPrompt);
        setPromptRefined(true);
      } else {
        alert("Failed to refine prompt: " + (data.error || "Unknown error"));
      }
    } catch (error) {
      console.error("Error refining prompt:", error);
      alert("Failed to refine prompt. Please try again.");
    } finally {
      setIsRefining(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
            🔬 AI Prompt Refinement
          </h1>
          <p className="text-muted-foreground mt-2">
            Transform your prompts with AI-powered refinement and custom filters
          </p>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>📝 Enter Your Prompt</CardTitle>
                <CardDescription>Start with your initial idea or question</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Textarea
                  value={naivePrompt}
                  onChange={(e) => setNaivePrompt(e.target.value)}
                  placeholder="Enter your prompt here..."
                  className="min-h-[120px]"
                  rows={5}
                />
                <div className="flex flex-wrap gap-2">
                  <Button
                    onClick={handleGenerateFilters}
                    disabled={isGeneratingFilters || isRefining || !naivePrompt.trim()}
                  >
                    <Sparkles className="w-4 h-4 mr-2" />
                    {isGeneratingFilters ? "Generating..." : "Generate Custom Filters"}
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => handleRefinePrompt(false)}
                    disabled={isGeneratingFilters || isRefining || !naivePrompt.trim()}
                  >
                    <Wand2 className="w-4 h-4 mr-2" />
                    {isRefining ? "Refining..." : "Refine Directly"}
                  </Button>
                </div>
                {filtersGenerated && (
                  <div className="flex items-center gap-2 text-sm text-green-600 dark:text-green-400">
                    <CheckCircle className="w-4 h-4" />
                    <span>Custom filters generated successfully!</span>
                  </div>
                )}
              </CardContent>
            </Card>

            <FileUpload onFilesProcessed={setExtractedText} />

            <FilterPanel
              defaultFilters={defaultFilters}
              setDefaultFilters={setDefaultFilters}
              customFilters={customFilters}
              customFilterValues={customFilterValues}
              setCustomFilterValues={setCustomFilterValues}
            />

            {customFilters.length > 0 && (
              <Button
                onClick={() => handleRefinePrompt(true)}
                disabled={isGeneratingFilters || isRefining || !naivePrompt.trim()}
                className="w-full"
                size="lg"
              >
                <Wand2 className="w-5 h-5 mr-2" />
                {isRefining ? "Refining..." : "Refine Prompt with All Filters"}
              </Button>
            )}
          </div>

          <div className="lg:sticky lg:top-4 lg:h-[calc(100vh-120px)]">
            <ChatInterface
              refinedPrompt={promptRefined ? refinedPrompt : undefined}
              onRefinedPromptUsed={() => setPromptRefined(false)}
            />
          </div>
        </div>


      </main>
    </div>
  );
}
