"use client";

import { useState } from "react";
import { ChevronDown, ChevronRight } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { RadioGroup } from "@/components/ui/radio-group";
import { Checkbox } from "@/components/ui/checkbox";
import { Slider } from "@/components/ui/slider";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { DefaultFilters, CustomFilter } from "@/types";

interface FilterPanelProps {
  defaultFilters: DefaultFilters;
  setDefaultFilters: (filters: DefaultFilters) => void;
  customFilters: CustomFilter[];
  customFilterValues: Record<string, any>;
  setCustomFilterValues: (values: Record<string, any>) => void;
}

export function FilterPanel({
  defaultFilters,
  setDefaultFilters,
  customFilters,
  customFilterValues,
  setCustomFilterValues,
}: FilterPanelProps) {
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    response: true,
    audience: true,
    additional: false,
  });

  const toggleSection = (section: string) => {
    setExpandedSections((prev) => ({ ...prev, [section]: !prev[section] }));
  };

  const renderCustomFilter = (filter: CustomFilter) => {
    const value = customFilterValues[filter.key];

    if (filter.type === "text_input") {
      return (
        <Textarea
          value={(value as string) || ""}
          onChange={(e) =>
            setCustomFilterValues({ ...customFilterValues, [filter.key]: e.target.value })
          }
          placeholder={filter.label}
          rows={3}
        />
      );
    }

    if (filter.type === "radio" && filter.options) {
      return (
        <RadioGroup
          name={filter.key}
          options={filter.options.map((opt) =>
            typeof opt === "string" ? { label: opt, value: opt } : opt
          )}
          value={value as string}
          onChange={(val) =>
            setCustomFilterValues({ ...customFilterValues, [filter.key]: val })
          }
        />
      );
    }

    if (filter.type === "checkbox") {
      if (!filter.options) {
        return (
          <Checkbox
            checked={(value as boolean) || false}
            onChange={(e) =>
              setCustomFilterValues({ ...customFilterValues, [filter.key]: e.target.checked })
            }
          />
        );
      }

      return (
        <div className="space-y-2">
          {filter.options.map((opt) => {
            const optValue = typeof opt === "string" ? opt : opt.value;
            const optLabel = typeof opt === "string" ? opt : opt.label;
            const selected = (value as string[]) || [];

            return (
              <Checkbox
                key={optValue}
                label={optLabel}
                checked={selected.includes(optValue)}
                onChange={(e) => {
                  const newSelected = e.target.checked
                    ? [...selected, optValue]
                    : selected.filter((v) => v !== optValue);
                  setCustomFilterValues({ ...customFilterValues, [filter.key]: newSelected });
                }}
              />
            );
          })}
        </div>
      );
    }

    if (filter.type === "selectbox" && filter.options) {
      return (
        <select
          value={(value as string) || ""}
          onChange={(e) =>
            setCustomFilterValues({ ...customFilterValues, [filter.key]: e.target.value })
          }
          className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
        >
          <option value="">Select...</option>
          {filter.options.map((opt) => {
            const optValue = typeof opt === "string" ? opt : opt.value;
            const optLabel = typeof opt === "string" ? opt : opt.label;
            return (
              <option key={optValue} value={optValue}>
                {optLabel}
              </option>
            );
          })}
        </select>
      );
    }

    if (filter.type === "slider") {
      return (
        <div className="space-y-4 pt-4">
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">
              {filter.min ?? 0}
            </span>
            <span className="font-medium">
              {(value as number) || filter.min || 0}
            </span>
            <span className="text-sm text-muted-foreground">
              {filter.max ?? 100}
            </span>
          </div>
          <Slider
            value={(value as number) || filter.min || 0}
            onChange={(val) =>
              setCustomFilterValues({ ...customFilterValues, [filter.key]: val })
            }
            min={filter.min ?? 0}
            max={filter.max ?? 100}
            step={filter.step ?? 1}
          />
        </div>
      );
    }

    return null;
  };

  const Section = ({
    title,
    section,
    children,
  }: {
    title: string;
    section: string;
    children: React.ReactNode;
  }) => (
    <div className="border rounded-md overflow-hidden">
      <Button
        variant="ghost"
        onClick={() => toggleSection(section)}
        className="w-full justify-between p-4 h-auto hover:bg-secondary"
      >
        <span className="font-medium">{title}</span>
        {expandedSections[section] ? (
          <ChevronDown className="w-4 h-4" />
        ) : (
          <ChevronRight className="w-4 h-4" />
        )}
      </Button>
      {expandedSections[section] && <div className="p-4 space-y-4 border-t">{children}</div>}
    </div>
  );

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>⚙️ Default Filters</CardTitle>
          <CardDescription>Configure your preferences</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Section title="Response Settings" section="response">
            <div className="space-y-2">
              <label className="text-sm font-medium">Answer Format</label>
              <RadioGroup
                name="answerFormat"
                options={[
                  { label: "Paragraph", value: "Paragraph" },
                  { label: "Bullet Points", value: "Bullet Points" },
                ]}
                value={defaultFilters.answerFormat}
                onChange={(val) =>
                  setDefaultFilters({ ...defaultFilters, answerFormat: val as any })
                }
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Tone of Response</label>
              <RadioGroup
                name="toneOfResponse"
                options={[
                  { label: "Formal", value: "Formal" },
                  { label: "Informal", value: "Informal" },
                  { label: "Neutral", value: "Neutral" },
                ]}
                value={defaultFilters.toneOfResponse}
                onChange={(val) =>
                  setDefaultFilters({ ...defaultFilters, toneOfResponse: val as any })
                }
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">
                Output Detail Level: {defaultFilters.outputDetail}
              </label>
              <Slider
                value={defaultFilters.outputDetail}
                onChange={(val) => setDefaultFilters({ ...defaultFilters, outputDetail: val })}
                min={1}
                max={5}
                step={1}
              />
            </div>
          </Section>

          <Section title="Audience & Purpose" section="audience">
            <div className="space-y-2">
              <label className="text-sm font-medium">Intended Audience</label>
              <RadioGroup
                name="audienceLevel"
                options={[
                  { label: "General", value: "General" },
                  { label: "Beginner", value: "Beginner" },
                  { label: "Intermediate", value: "Intermediate" },
                  { label: "Expert", value: "Expert" },
                ]}
                value={defaultFilters.audienceLevel}
                onChange={(val) =>
                  setDefaultFilters({ ...defaultFilters, audienceLevel: val as any })
                }
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Primary Purpose</label>
              <select
                value={defaultFilters.purpose}
                onChange={(e) =>
                  setDefaultFilters({ ...defaultFilters, purpose: e.target.value as any })
                }
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              >
                <option value="Learning/Education">Learning/Education</option>
                <option value="Professional/Work">Professional/Work</option>
                <option value="Personal Interest">Personal Interest</option>
                <option value="Research">Research</option>
              </select>
            </div>
          </Section>

          <Section title="Additional Preferences" section="additional">
            <Checkbox
              label="Include Visuals"
              checked={defaultFilters.includeVisuals}
              onChange={(e) =>
                setDefaultFilters({ ...defaultFilters, includeVisuals: e.target.checked })
              }
            />

            <div className="space-y-2">
              <label className="text-sm font-medium">Response Structure</label>
              <RadioGroup
                name="responseStructure"
                options={[
                  { label: "Concise", value: "Concise" },
                  { label: "Structured with Headings", value: "Structured with Headings" },
                  { label: "Step-by-Step", value: "Step-by-Step" },
                ]}
                value={defaultFilters.responseStructure}
                onChange={(val) =>
                  setDefaultFilters({ ...defaultFilters, responseStructure: val as any })
                }
              />
            </div>
          </Section>
        </CardContent>
      </Card>

      {customFilters.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>🎯 Custom Filters</CardTitle>
            <CardDescription>Domain-specific preferences for your prompt</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {customFilters.map((filter) => (
              <div key={filter.key} className="space-y-2">
                <label className="text-sm font-medium">{filter.label}</label>
                {renderCustomFilter(filter)}
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
