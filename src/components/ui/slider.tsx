"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

export interface SliderProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'onChange'> {
  value?: number;
  onChange?: (value: number) => void;
  min?: number;
  max?: number;
  step?: number;
}

const Slider = React.forwardRef<HTMLInputElement, SliderProps>(
  ({ className, value, onChange, min = 0, max = 100, step = 1, ...props }, ref) => {
    return (
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange?.(Number(e.target.value))}
        className={cn(
          "w-full h-2 bg-secondary rounded-lg appearance-none cursor-pointer accent-primary focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
          className
        )}
        ref={ref}
        {...props}
      />
    );
  }
);
Slider.displayName = "Slider";

export { Slider };
