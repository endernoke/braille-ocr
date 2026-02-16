import { useCallback, useRef, useState, type DragEvent } from "react";
import { Upload, X, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";

interface UploadSectionProps {
  onSubmit: (file: File) => void;
  isLoading: boolean;
}

export function UploadSection({ onSubmit, isLoading }: UploadSectionProps) {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback((f: File) => {
    setFile(f);
    const url = URL.createObjectURL(f);
    setPreview(url);
  }, []);

  const clearFile = useCallback(() => {
    if (preview) URL.revokeObjectURL(preview);
    setFile(null);
    setPreview(null);
    if (inputRef.current) inputRef.current.value = "";
  }, [preview]);

  const handleDrop = useCallback(
    (e: DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      const dropped = e.dataTransfer.files[0];
      if (dropped && dropped.type.startsWith("image/")) {
        handleFile(dropped);
      }
    },
    [handleFile]
  );

  const handleDragOver = useCallback((e: DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setDragOver(false);
  }, []);

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const selected = e.target.files?.[0];
      if (selected) handleFile(selected);
    },
    [handleFile]
  );

  const handleSubmit = () => {
    if (file) onSubmit(file);
  };

  return (
    <section id="upload" className="mx-auto max-w-2xl px-4 py-16">
      <h2 className="text-2xl font-semibold tracking-tight">
        Upload &amp; transcribe
      </h2>

      <div className="mt-6">
        {!preview ? (
          <div
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onClick={() => inputRef.current?.click()}
            className={`flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed p-12 text-center transition-colors ${
              dragOver
                ? "border-primary bg-primary/5"
                : "border-border hover:border-muted-foreground/40"
            }`}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === " ") inputRef.current?.click();
            }}
          >
            <Upload className="size-8 text-muted-foreground" />
            <p className="mt-3 text-sm text-muted-foreground">
              Drag &amp; drop an image or click to browse
            </p>
            <p className="mt-1 text-xs text-muted-foreground/60">
              JPG, PNG, HEIC supported
            </p>
          </div>
        ) : (
          <div className="relative">
            <div className="overflow-hidden rounded-xl border">
              <img
                src={preview}
                alt="Uploaded braille image preview"
                className="mx-auto max-h-64 w-auto object-contain"
              />
            </div>
            <button
              onClick={clearFile}
              className="absolute right-2 top-2 rounded-full bg-background/80 p-1.5 text-muted-foreground shadow-sm backdrop-blur transition-colors hover:text-foreground"
              aria-label="Remove image"
            >
              <X className="size-4" />
            </button>
          </div>
        )}

        <input
          ref={inputRef}
          type="file"
          accept="image/*"
          capture="environment"
          onChange={handleChange}
          className="hidden"
        />
      </div>

      {/* Language selector - for future backend support */}
      {/* <div className="mt-4">
        <label className="text-sm font-medium">
          Braille language{" "}
          <span className="text-muted-foreground">(optional)</span>
        </label>
      </div> */}

      <Button
        onClick={handleSubmit}
        disabled={!file || isLoading}
        className="mt-4 w-full sm:w-auto"
        size="lg"
      >
        {isLoading ? (
          <>
            <Loader2 className="size-4 animate-spin" />
            Processing…
          </>
        ) : (
          "Transcribe"
        )}
      </Button>
    </section>
  );
}
