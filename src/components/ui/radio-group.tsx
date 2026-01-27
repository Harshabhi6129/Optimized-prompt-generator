"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

export interface RadioOption {
  label: string;
  value: string;
}

export interface RadioGroupProps {
  options: RadioOption[];
  value?: string;
  onChange?: (value: string) => void;
  name: string;
  className?: string;
}

const RadioGroup = React.forwardRef<HTMLDivElement, RadioGroupProps>(
  ({ options, value, onChange, name, className }, ref) => {
    return (
      <div ref={ref} className={cn("space-y-2", className)}>
        {options.map((option) => {
          const radioId = `${name}-${option.value}`;
          return (
            <div key={option.value} className="flex items-center space-x-2">
              <input
                type="radio"
                id={radioId}
                name={name}
                value={option.value}
                checked={value === option.value}
                onChange={(e) => onChange?.(e.target.value)}
                className="h-4 w-4 border-input text-primary focus:ring-2 focus:ring-ring focus:ring-offset-2"
              />
              <label
                htmlFor={radioId}
                className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
              >
                {option.label}
              </label>
            </div>
          );
        })}
      </div>
    );
  }
);
RadioGroup.displayName = "RadioGroup";

export interface RadioGroupItemProps extends React.InputHTMLAttributes<HTMLInputElement> {
  value: string;
}

const RadioGroupItem = React.forwardRef<HTMLInputElement, RadioGroupItemProps>(
  ({ className, ...props }, ref) => {
    return (
      <input
        type="radio"
        className={cn(
          "h-4 w-4 rounded-full border-input text-primary focus:ring-2 focus:ring-ring focus:ring-offset-2",
          className
        )}
        ref={ref}
        {...props}
      />
    );
  }
);
RadioGroupItem.displayName = "RadioGroupItem";

export { RadioGroup, RadioGroupItem };
