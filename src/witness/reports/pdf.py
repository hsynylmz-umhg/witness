"""Optional local HTML-to-PDF rendering with a safe HTML-only fallback."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PdfResult:
    """The PDF path or the explicit HTML-only fallback record."""

    pdf_path: Path | None
    blocker_path: Path | None
    blocker: str | None


def render_pdf(html_document: bytes, output_path: Path) -> PdfResult:
    """Use optional WeasyPrint when installed; otherwise record an HTML-only fallback."""
    try:
        from weasyprint import HTML
    except ImportError:
        blocker_path = output_path.with_suffix(".pdf.blocked.txt")
        blocker = (
            "PDF not produced: optional WeasyPrint is unavailable; report.html is the fallback."
        )
        blocker_path.write_text(blocker + "\n", encoding="utf-8", newline="\n")
        return PdfResult(None, blocker_path, blocker)
    try:
        HTML(string=html_document.decode("utf-8")).write_pdf(output_path)
    except (OSError, UnicodeError, ValueError) as error:
        blocker_path = output_path.with_suffix(".pdf.blocked.txt")
        blocker = (
            f"PDF not produced: WeasyPrint failed ({type(error).__name__}); "
            "report.html is the fallback."
        )
        blocker_path.write_text(blocker + "\n", encoding="utf-8", newline="\n")
        return PdfResult(None, blocker_path, blocker)
    return PdfResult(output_path, None, None)
