import { Camera, Languages, FileText } from "lucide-react";
import { FullScreenImageViewer } from "@/components/FullScreenImageViewer";

const steps = [
  {
    icon: Camera,
    title: "Upload a photo",
    description: "Take or upload a clear photo of the braille text. See tips below for best results.",
  },
  {
    icon: Languages,
    title: "Select language",
    description: "Optionally choose the braille language, or let us auto-detect. Currently supports English UEB and Cantonese Braille. More to come!",
  },
  {
    icon: FileText,
    title: "Get transcription",
    description: "Receive the recognized text and Braille patterns.",
  },
];

const tips = [
  "Ensure lighting falls from the front or upper left. Chaos will ensue otherwise.",
  "There should be clear contrast between dots and paper.",
  "Shoot from directly above so the angle is roughly perpendicular to the page.",
  "Keep the entire page in view if possible and avoid irrelevant background clutter.",
];

export function HowToUse() {
  return (
    <section className="mx-auto max-w-4xl px-4 pt-16">
      <h2 className="text-2xl font-semibold tracking-tight">How to use</h2>

      <div className="mt-8 grid gap-4 sm:grid-cols-3">
        {steps.map((step, i) => (
          <div
            key={i}
            className="rounded-lg border p-5"
          >
            <step.icon className="size-5 text-muted-foreground" />
            <h3 className="mt-3 text-sm font-semibold">{step.title}</h3>
            <p className="mt-1 text-sm leading-relaxed text-muted-foreground">
              {step.description}
            </p>
          </div>
        ))}
      </div>

      {/* Photo Taking Tips */}
      <div className="mt-10 rounded-xl border-2 bg-muted/20 p-6 sm:p-8">
        <h3 className="text-lg font-semibold tracking-tight">
          Tips for best results
        </h3>
        
        <div className="mt-6 flex flex-col gap-6 lg:flex-row lg:items-center lg:gap-10">
          <div className="shrink-0 lg:w-[45%]">
            <FullScreenImageViewer
              src="/photo-taking-illustration.png"
              alt="Illustration showing proper photo-taking technique for braille text, full size"
            >
              <button className="w-full overflow-hidden rounded-lg border bg-background focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2">
                <img
                  src="/photo-taking-illustration.png"
                  alt="Illustration showing proper photo-taking technique for braille text, click to enlarge"
                  className="w-full"
                />
              </button>
            </FullScreenImageViewer>
          </div>

          <ul className="flex-1 space-y-3 text-sm leading-relaxed">
            {tips.map((tip, i) => (
              <li key={i} className="flex gap-3">
                <span className="mt-0.5 shrink-0 font-semibold text-foreground">•</span>
                <span className="text-foreground/90">{tip}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}
