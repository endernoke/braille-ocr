import type { ReactNode } from "react";
import {
  Dialog,
  DialogContent,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

interface FullScreenImageViewerProps {
  src: string;
  alt: string;
  title?: string;
  children: ReactNode;
}

export function FullScreenImageViewer({
  src,
  alt,
  title = "Image preview",
  children,
}: FullScreenImageViewerProps) {
  return (
    <Dialog>
      <DialogTrigger asChild>{children}</DialogTrigger>
      <DialogContent className="flex h-dvh w-dvw min-h-[100vh] min-w-[100vw] items-center justify-center border-0 bg-transparent p-0 ring-0">
        <DialogTitle className="sr-only">{title}</DialogTitle>
        <img
          src={src}
          alt={alt}
          className="h-[90vh] max-h-[90vh] w-[90vw] max-w-[90vw] object-contain"
        />
      </DialogContent>
    </Dialog>
  );
}
