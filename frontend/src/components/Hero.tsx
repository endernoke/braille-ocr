import { ArrowDown } from "lucide-react";

export function Hero() {
  const scrollToUpload = () => {
    document.getElementById("upload")?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <section className="mx-auto max-w-2xl px-4 py-20 text-center sm:py-28">
      <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">
        Convert braille photos to text
      </h1>
      <p className="mt-4 text-base leading-relaxed text-muted-foreground sm:text-lg">
        Take a photo of a braille page, upload it here, and get a print-text
        transcription in seconds — along with detected characters and an
        annotated image showing where each character was found.
      </p>
      <button
        onClick={scrollToUpload}
        className="mt-8 inline-flex items-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-foreground"
      >
        Get started
        <ArrowDown className="size-4" />
      </button>
    </section>
  );
}
