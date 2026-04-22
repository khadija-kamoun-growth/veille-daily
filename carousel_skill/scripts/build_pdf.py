#!/usr/bin/env python3
"""Render a Linkedin Caroussels HTML playbook into a PDF + quick previews.

Usage:
    python build_pdf.py <playbook.html> [--out <output.pdf>] [--preview-dpi 160]

The script always runs WeasyPrint from the directory containing the HTML file,
because the template uses relative asset paths like ``assets/apollo-mark.png``.
Running from any other directory causes FileNotFoundError on the images.

After rendering the PDF, it drops two preview PNGs (cover + close) next to the
PDF so you can eyeball the output without opening the full document.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("html", type=Path, help="Path to the playbook HTML file")
    parser.add_argument("--out", type=Path, default=None, help="Output PDF path (default: alongside the HTML)")
    parser.add_argument("--preview-dpi", type=int, default=160, help="DPI for the preview PNGs")
    parser.add_argument("--no-preview", action="store_true", help="Skip generating preview PNGs")
    args = parser.parse_args()

    html_path: Path = args.html.resolve()
    if not html_path.exists():
        print(f"error: html file not found: {html_path}", file=sys.stderr)
        return 1

    out_pdf: Path = args.out.resolve() if args.out else html_path.with_suffix(".pdf")
    out_pdf.parent.mkdir(parents=True, exist_ok=True)

    # Render: cd into the HTML's folder so relative asset paths work.
    prev_cwd = os.getcwd()
    try:
        os.chdir(html_path.parent)
        try:
            from weasyprint import HTML
        except ImportError:
            print(
                "error: weasyprint is not installed. Install with:\n"
                "    pip install weasyprint --break-system-packages",
                file=sys.stderr,
            )
            return 2

        print(f"Rendering {html_path.name} -> {out_pdf}")
        HTML(html_path.name).write_pdf(str(out_pdf))
        print(f"PDF written: {out_pdf} ({out_pdf.stat().st_size // 1024} KB)")
    finally:
        os.chdir(prev_cwd)

    if args.no_preview:
        return 0

    try:
        from pdf2image import convert_from_path
    except ImportError:
        print(
            "warning: pdf2image not installed; skipping previews.\n"
            "    pip install pdf2image --break-system-packages",
            file=sys.stderr,
        )
        return 0

    print(f"Generating previews at {args.preview_dpi} dpi...")
    pages = convert_from_path(str(out_pdf), dpi=args.preview_dpi)
    cover_path = out_pdf.with_name(out_pdf.stem + "__preview-cover.png")
    close_path = out_pdf.with_name(out_pdf.stem + "__preview-close.png")
    pages[0].save(cover_path)
    pages[-1].save(close_path)
    print(f"Cover preview: {cover_path}")
    print(f"Close preview: {close_path}")
    print(f"Pages: {len(pages)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
