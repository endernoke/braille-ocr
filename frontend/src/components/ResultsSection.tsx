import { Copy, Check } from "lucide-react";
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { FullScreenImageViewer } from "@/components/FullScreenImageViewer";
import type { JobResult } from "@/types/api";

interface ResultsSectionProps {
  result: JobResult | null;
  isLoading: boolean;
  error: string | null;
  onDismissError: () => void;
}

export function ResultsSection({
  result,
  isLoading,
  error,
  onDismissError,
}: ResultsSectionProps) {
  const [copied, setCopied] = useState(false);

  if (!isLoading && !result && !error) return null;

  const handleCopy = async () => {
    if (!result) return;
    await navigator.clipboard.writeText(result.extracted_text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <section id="results" className="mx-auto max-w-4xl px-4 pb-20 pt-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
      {error && (
        <div className="mb-6 flex items-start justify-between rounded-lg border border-destructive/30 bg-destructive/10 p-4 text-sm text-destructive">
          <p>{error}</p>
          <button
            onClick={onDismissError}
            className="ml-4 shrink-0 text-destructive/70 hover:text-destructive"
            aria-label="Dismiss error"
          >
            ✕
          </button>
        </div>
      )}

      {isLoading && (
        <div className="space-y-4">
          <Skeleton className="h-32 w-full rounded-lg" />
          <Skeleton className="h-16 w-full rounded-lg" />
          <Skeleton className="h-48 w-full rounded-lg" />
        </div>
      )}

      {result && !isLoading && (
        <div className="space-y-4">
          {/* Text Transcription */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
              <CardTitle className="text-base font-semibold">
                Transcription
              </CardTitle>
              <button
                onClick={handleCopy}
                className="inline-flex items-center gap-1.5 text-xs text-muted-foreground transition-colors hover:text-foreground"
                aria-label="Copy transcription"
              >
                {copied ? (
                  <>
                    <Check className="size-3.5" />
                    Copied
                  </>
                ) : (
                  <>
                    <Copy className="size-3.5" />
                    Copy
                  </>
                )}
              </button>
            </CardHeader>
            <CardContent>
              <pre className="whitespace-pre-wrap rounded-md bg-muted p-4 font-mono text-sm leading-relaxed">
                {result.extracted_text}
              </pre>
              {result.classification && (
                <p className="mt-3 text-xs text-muted-foreground">
                  Detected as:{" "}
                  <span className="font-medium text-foreground">
                    {result.classification}
                  </span>
                  {result.confidence != null && (
                    <span>
                      {" "}
                      · {(result.confidence * 100).toFixed(1)}% confidence
                    </span>
                  )}
                </p>
              )}
            </CardContent>
          </Card>

          {result.bounding_boxes.length > 0 && (
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base font-semibold">
                  Detected characters
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-1.5">
                  {result.bounding_boxes.map((box, i) => (
                    <Badge
                      key={i}
                      variant="secondary"
                      className="font-mono text-xs"
                    >
                      {box.text}
                      {box.confidence < 1 && (
                        <span className="ml-1 text-muted-foreground">
                          {(box.confidence * 100).toFixed(0)}%
                        </span>
                      )}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {result.annotated_image_url && (
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base font-semibold">
                  Annotated image
                </CardTitle>
              </CardHeader>
              <CardContent>
                <FullScreenImageViewer
                  src={result.annotated_image_url}
                  alt="Annotated braille image with bounding boxes, full size"
                  title="Annotated image full view"
                >
                  <button className="group relative w-full overflow-hidden rounded-lg border">
                    <img
                      src={result.annotated_image_url}
                      alt="Annotated braille image with bounding boxes, click to enlarge"
                      className="w-full object-contain"
                    />
                  </button>
                </FullScreenImageViewer>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </section>
  );
}
