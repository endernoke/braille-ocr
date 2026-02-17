import { useState, useCallback } from "react";
import { Header } from "@/components/Header";
import { Hero } from "@/components/Hero";
import { HowToUse } from "@/components/HowToUse";
import { UploadSection } from "@/components/UploadSection";
import { ResultsSection } from "@/components/ResultsSection";
import { Footer } from "@/components/Footer";
import { submitJob, pollJobUntilDone } from "@/services/api";
import type { BrailleLanguage, JobResult } from "@/types/api";

export default function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<JobResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = useCallback(async (file: File, language?: BrailleLanguage | null) => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const { job_id } = await submitJob(file, language);
      const status = await pollJobUntilDone(job_id);

      if (status.result) {
        setResult(status.result);
        // Scroll to results after a brief delay for the DOM to render
        setTimeout(() => {
          document
            .getElementById("results")
            ?.scrollIntoView({ behavior: "smooth" });
        }, 100);
      } else {
        setError("No result returned from the server.");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "An unexpected error occurred.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleDismissError = useCallback(() => {
    setError(null);
  }, []);

  return (
    <div className="min-h-screen bg-background text-foreground">
      <Header />
      <main>
        <Hero />
        <HowToUse />
        <UploadSection onSubmit={handleSubmit} isLoading={isLoading} />
        <ResultsSection
          result={result}
          isLoading={isLoading}
          error={error}
          onDismissError={handleDismissError}
        />
      </main>
      <Footer />
    </div>
  );
}
