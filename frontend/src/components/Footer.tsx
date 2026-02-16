const GITHUB_URL = "https://github.com/endernoke/braille-ocr";

export function Footer() {
  return (
    <footer className="border-t py-8 text-center text-sm text-muted-foreground">
      <p>
        Built with ♥ ·{" "}
        <a
          href={GITHUB_URL}
          target="_blank"
          rel="noopener noreferrer"
          className="underline underline-offset-4 transition-colors hover:text-foreground"
        >
          GitHub
        </a>
      </p>
    </footer>
  );
}
