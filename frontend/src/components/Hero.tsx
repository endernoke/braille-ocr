import { Camera, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { FullScreenImageViewer } from "@/components/FullScreenImageViewer";

const SAMPLE_IMAGE = "/sample-braille-image.jpg";
const SAMPLE_TEXT = "... Item: 8.4\nno passengers were on board: the catamaran was\ntraining new crew members\nDF page reference: 7 ...";

export function Hero() {
  const scrollToUpload = () => {
    const uploadSection = document.getElementById("upload");
    const uploadHeading = document.getElementById("upload-heading");
    uploadSection?.scrollIntoView({ behavior: "smooth" });
    // For keyboard focus / screen readers
    uploadHeading?.focus({ preventScroll: true });
  };

  return (
    <section className="mx-auto max-w-4xl px-4 pt-20 pb-10">
      <div className="flex flex-col items-start gap-12 lg:flex-row lg:items-center lg:gap-16">
        {/* Left: copy + CTA */}
        <div className="flex-1">
          <h1 className="text-4xl font-bold tracking-tight md:text-5xl">
            Convert braille photos to text
          </h1>
          <p className="mt-4 text-base leading-relaxed text-muted-foreground sm:text-lg">
            Take a photo of a braille page, upload it here, and get a print-text
            transcription in seconds.
          </p>
          <p className="mt-3 text-xs text-muted-foreground/70">
            English UEB Grade 1 & 2 · Cantonese Braille · Single & double-sided pages
          </p>
          <Button
            onClick={scrollToUpload}
            size="lg"
            className="mt-6 gap-2"
          >
            <Camera className="size-4" />
            Upload a photo
          </Button>
        </div>

        {/* Right: sample output */}
        <div
          className="w-full max-w-sm shrink-0 lg:w-[45%]"
          role="group"
          aria-label="Sample braille transcription output"
        >
          <p className="mb-2 text-xs font-medium uppercase tracking-wider text-muted-foreground/60">
            Example result
          </p>
          <div className="flex items-stretch gap-3 rounded-xl border bg-muted/30 p-3">
            {/* Sample braille image */}
            <FullScreenImageViewer
              src={SAMPLE_IMAGE}
              alt="Sample braille text photo"
            >
              <div className="flex w-2/5 shrink-0 items-center overflow-hidden rounded-lg border bg-background">
                <img
                  src={SAMPLE_IMAGE}
                  alt="Sample braille text photo, click to enlarge"
                  className="size-full object-cover"
                />
              </div>
            </FullScreenImageViewer>

            <div className="flex shrink-0 items-center">
              <ArrowRight className="size-4 text-muted-foreground/50" />
            </div>

            {/* Sample transcription */}
            <div className="flex min-w-0 flex-1 items-center">
              <pre className="whitespace-pre-wrap text-xs leading-relaxed text-muted-foreground">
                {SAMPLE_TEXT}
              </pre>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
