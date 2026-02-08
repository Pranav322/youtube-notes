'use client';

import { useState, useEffect } from 'react';
import { NoteInput } from '@/components/NoteInput';
import { NoteViewer } from '@/components/NoteViewer';
import { createNote, Note } from '@/lib/api';

export default function Home() {
  const [note, setNote] = useState<Note | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [statusText, setStatusText] = useState('');
  const [error, setError] = useState<string | null>(null);

  // Status simulation effect
  useEffect(() => {
    if (!isLoading) {
      setStatusText('');
      return;
    }

    const statuses = [
      "Initializing AI Agent...",
      "Extracting Video Transcript...",
      "Analyzing Technical Concepts...",
      "Formatting Code Blocks...",
      "Finalizing Markdown Structure..."
    ];

    let currentIndex = 0;
    setStatusText(statuses[0]);

    const interval = setInterval(() => {
      currentIndex = (currentIndex + 1) % statuses.length;
      setStatusText(statuses[currentIndex]);
    }, 3500); // Change status every 3.5 seconds

    return () => clearInterval(interval);
  }, [isLoading]);

  const handleSubmit = async (url: string) => {
    setIsLoading(true);
    setError(null);
    setNote(null);

    try {
      const data = await createNote(url, false);
      setNote(data);
    } catch (err: any) {
      console.error(err);
      const msg = err.response?.data?.detail || 'Something went wrong. Please check the URL and try again.';
      setError(typeof msg === 'string' ? msg : JSON.stringify(msg));
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegenerate = async () => {
    if (!note) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = await createNote(note.url, true);
      setNote(data);
    } catch (err: any) {
      console.error(err);
      const msg = err.response?.data?.detail || 'Something went wrong during regeneration.';
      setError(typeof msg === 'string' ? msg : JSON.stringify(msg));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-background text-foreground font-sans selection:bg-primary/20">
      <div className="max-w-5xl mx-auto px-6 py-16 space-y-12">
        <div className="text-center space-y-6">
          <h1 className="text-5xl md:text-6xl font-black tracking-tight text-foreground">
            YouTube <span className="text-primary relative inline-block">
              Technical
              <span className="absolute bottom-2 left-0 w-full h-3 bg-primary/20 -z-10 rotate-1"></span>
            </span> Note-Taker
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
            Transform complex technical videos into beautiful, structured Markdown notes with preserved code blocks and mathematical formulas.
          </p>
        </div>

        <NoteInput
          onSubmit={handleSubmit}
          isLoading={isLoading}
          statusText={statusText}
        />

        {error && (
          <div className="p-6 rounded-xl bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-900/50 text-red-600 dark:text-red-400 text-center animate-in fade-in slide-in-from-top-2">
            <p className="font-medium">{error}</p>
          </div>
        )}

        {note && (
          <div className="animate-in fade-in slide-in-from-bottom-8 duration-700">
            <NoteViewer
              content_detailed={note.content_detailed}
              input_tokens={note.input_tokens}
              output_tokens={note.output_tokens}
              generation_cost={note.generation_cost}
              onRegenerate={handleRegenerate}
            />
          </div>
        )}
      </div>
    </main>
  );
}
