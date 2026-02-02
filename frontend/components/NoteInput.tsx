'use client';

import { useState } from 'react';
import { Loader2, ArrowRight, Sparkles } from 'lucide-react';
import { twMerge } from 'tailwind-merge';

interface NoteInputProps {
  onSubmit: (url: string) => Promise<void>;
  isLoading: boolean;
  statusText: string;
}

export function NoteInput({ onSubmit, isLoading, statusText }: NoteInputProps) {
  const [url, setUrl] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (url.trim()) {
      onSubmit(url);
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto mb-12">
      <form onSubmit={handleSubmit} className="relative z-10">
        <div className="relative flex items-center shadow-lg rounded-xl transition-shadow duration-300 hover:shadow-xl hover:shadow-primary/5 group">
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Paste YouTube URL here..."
            className={twMerge(
              "w-full pl-6 pr-40 py-4 text-lg rounded-xl border-2 transition-all duration-300",
              "bg-background text-foreground",
              "border-muted focus:border-primary focus:ring-4 focus:ring-primary/10 focus:outline-none",
              "placeholder:text-muted-foreground",
              isLoading ? "opacity-60 cursor-not-allowed" : ""
            )}
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !url}
            className={twMerge(
              "absolute right-2 px-6 py-2.5 rounded-lg font-semibold text-sm",
              "bg-primary text-primary-foreground",
              "hover:bg-primary/90 hover:scale-105 active:scale-95",
              "disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100",
              "transition-all duration-200 flex items-center gap-2 shadow-md",
              "uppercase tracking-wide"
            )}
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <>
                Generate
                <Sparkles className="w-4 h-4" />
              </>
            )}
          </button>
        </div>
      </form>
      
      {isLoading && (
        <div className="mt-6 flex flex-col items-center gap-3 animate-in fade-in slide-in-from-top-4 duration-500">
          <div className="flex items-center gap-2 text-primary font-medium">
             <Loader2 className="w-4 h-4 animate-spin" />
             <span className="animate-pulse">{statusText}</span>
          </div>
          <div className="w-64 h-1 bg-muted rounded-full overflow-hidden">
             <div className="h-full bg-primary animate-progress-indeterminate rounded-full"></div>
          </div>
        </div>
      )}
    </div>
  );
}
