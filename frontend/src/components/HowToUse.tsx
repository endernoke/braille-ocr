import { Camera, Languages, FileText, ChevronDown } from "lucide-react";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { useState } from "react";

const steps = [
  {
    icon: Camera,
    title: "Upload a photo",
    description: "Take or upload a clear photo of the braille text.",
  },
  {
    icon: Languages,
    title: "Select language",
    description: "Optionally choose the braille language, or let us auto-detect.",
  },
  {
    icon: FileText,
    title: "Get transcription",
    description: "Receive the print text, detected characters, and an annotated image.",
  },
];

const tips = [
  "Use even, diffused lighting — avoid harsh shadows and glare.",
  "Keep the braille page as flat as possible.",
  "Fill the frame with the braille text for best resolution.",
  "Shoot from directly above so the angle is perpendicular to the page.",
  "Ensure dots are clearly visible; high contrast between dots and paper helps.",
];

export function HowToUse() {
  const [tipsOpen, setTipsOpen] = useState(false);

  return (
    <section className="mx-auto max-w-4xl px-4 py-16">
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

      <Collapsible open={tipsOpen} onOpenChange={setTipsOpen} className="mt-6">
        <CollapsibleTrigger className="flex items-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-foreground">
          <ChevronDown
            className={`size-4 transition-transform ${tipsOpen ? "rotate-180" : ""}`}
          />
          Tips for best results
        </CollapsibleTrigger>
        <CollapsibleContent className="mt-3 rounded-lg bg-muted px-5 py-4">
          <ul className="space-y-2 text-sm leading-relaxed text-muted-foreground">
            {tips.map((tip, i) => (
              <li key={i} className="flex gap-2">
                <span className="mt-0.5 shrink-0 text-muted-foreground/60">•</span>
                {tip}
              </li>
            ))}
          </ul>
        </CollapsibleContent>
      </Collapsible>
    </section>
  );
}
