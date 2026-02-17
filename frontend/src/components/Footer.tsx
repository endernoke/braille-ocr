const AUTHOR_URL = "https://github.com/endernoke";
const AUTHOR_NAME = "@endernoke";

export function Footer() {
  return (
    <footer className="border-t py-4 text-center text-sm text-muted-foreground">
      <p>
        Built with ❤️ by {" "}
        <a
          href={AUTHOR_URL}
          target="_blank"
          rel="noopener noreferrer"
          className="underline underline-offset-4 transition-colors hover:text-foreground"
        >
          {AUTHOR_NAME}
        </a>
      </p>
    </footer>
  );
}
