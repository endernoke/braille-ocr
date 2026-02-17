import { Github } from "lucide-react";

const GITHUB_URL = "https://github.com/endernoke/braille-ocr";

export function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="mx-auto flex h-14 max-w-4xl items-center justify-between px-4">
        <span className="text-lg font-semibold tracking-tight">
          Braille OCR
        </span>
        <a
          href={GITHUB_URL}
          target="_blank"
          rel="noopener noreferrer"
          className="text-muted-foreground transition-colors hover:text-foreground"
          aria-label="View project on GitHub"
        >
          <Github className="size-5" aria-label="View project on GitHub"/>
        </a>
      </div>
    </header>
  );
}
