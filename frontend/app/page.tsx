'use client';

import { useState, useEffect } from 'react';
import { NoteInput } from '@/components/NoteInput';
import { NoteViewer } from '@/components/NoteViewer';
import { NotesGallery } from '@/components/NotesGallery';
import { createNote, listNotes, Note } from '@/lib/api';
import { AlertTriangle } from 'lucide-react';

interface RateLimitError {
  message: string;
  note: string;
  limit_reached: boolean;
}

export default function Home() {
  const [note, setNote] = useState<Note | null>(null);
  const [allNotes, setAllNotes] = useState<Note[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingNotes, setIsLoadingNotes] = useState(true);
  const [statusText, setStatusText] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [rateLimitError, setRateLimitError] = useState<RateLimitError | null>(null);

  // Fetch all notes on load
  useEffect(() => {
    loadNotes();
  }, []);

  const loadNotes = async () => {
    setIsLoadingNotes(true);
    try {
      const notes = await listNotes();
      setAllNotes(notes);
    } catch (err) {
      console.error('Failed to load notes:', err);
    } finally {
      setIsLoadingNotes(false);
    }
  };

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
    }, 3500);

    return () => clearInterval(interval);
  }, [isLoading]);

  const handleSubmit = async (url: string) => {
    setIsLoading(true);
    setError(null);
    setRateLimitError(null);
    setNote(null);

    try {
      const data = await createNote(url, false);
      setNote(data);
      loadNotes(); // Refresh gallery
    } catch (err: any) {
      console.error(err);
      const detail = err.response?.data?.detail;

      // Check if it's a rate limit error (429)
      if (err.response?.status === 429 && typeof detail === 'object') {
        setRateLimitError(detail as RateLimitError);
      } else {
        const msg = typeof detail === 'string' ? detail : 'Something went wrong. Please check the URL and try again.';
        setError(msg);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegenerate = async () => {
    if (!note) return;
    setIsLoading(true);
    setError(null);
    setRateLimitError(null);

    try {
      const data = await createNote(note.url, true);
      setNote(data);
      loadNotes();
    } catch (err: any) {
      console.error(err);
      const detail = err.response?.data?.detail;

      if (err.response?.status === 429 && typeof detail === 'object') {
        setRateLimitError(detail as RateLimitError);
      } else {
        const msg = typeof detail === 'string' ? detail : 'Something went wrong during regeneration.';
        setError(msg);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectNote = (selectedNote: Note) => {
    setNote(selectedNote);
    setError(null);
    setRateLimitError(null);
    // Scroll to top to show the note
    window.scrollTo({ top: 0, behavior: 'smooth' });
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

        {/* Rate Limit Error Banner */}
        {rateLimitError && (
          <div className="p-6 rounded-xl bg-amber-50 dark:bg-amber-900/10 border border-amber-200 dark:border-amber-900/50 animate-in fade-in slide-in-from-top-2">
            <div className="flex items-start gap-4">
              <AlertTriangle className="w-6 h-6 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-semibold text-amber-700 dark:text-amber-300">
                  {rateLimitError.message}
                </p>
                <p className="text-amber-600 dark:text-amber-400 text-sm mt-1">
                  {rateLimitError.note}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Generic Error */}
        {error && (
          <div className="p-6 rounded-xl bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-900/50 text-red-600 dark:text-red-400 text-center animate-in fade-in slide-in-from-top-2">
            <p className="font-medium">{error}</p>
          </div>
        )}

        {/* Current Note Viewer */}
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

        {/* Notes Gallery */}
        <div className="pt-8 border-t border-primary/10">
          <NotesGallery notes={allNotes} isLoading={isLoadingNotes} onSelectNote={handleSelectNote} />
        </div>
      </div>
    </main>
  );
}
