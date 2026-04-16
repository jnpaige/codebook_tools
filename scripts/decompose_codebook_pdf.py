"""
decompose_codebook_pdf.py — Split a compiled codebook PDF into per-trait page chunks

Takes a PDF produced from a codebook Rmd (with inline figures, as produced by
Procedural.unit.codebook.figures) and decomposes it into per-trait page sets.
Each trait's pages — the text entry plus any figures that follow it — are
extracted and saved as PNG images under a directory named for that trait.

The decomposition relies on the PDF's table of contents (bookmarks), which R
Markdown generates automatically from section headings when `toc: true` is set.
Level-2 headings (`##`) become TOC entries; the page range for each trait is
from its TOC page to the page before the next TOC entry at the same level or
higher.

Prerequisites
-------------
- The codebook PDF must have been compiled with `toc: true` and
  `number_sections: yes` so that section bookmarks are embedded.
- PyMuPDF (fitz) must be installed: pip install PyMuPDF

Usage
-----
  python decompose_codebook_pdf.py \\
      --pdf  path/to/codebook.pdf \\
      --out  path/to/output_dir \\
      [--dpi 150] \\
      [--section-level 2] \\
      [--skip-before "Traits"]

  --pdf             Path to the compiled codebook PDF.
  --out             Output directory.  One subdirectory per trait is created.
  --dpi             Render DPI for page images (default: 150).
  --section-level   TOC level of trait headings (default: 2 for ## headings).
  --skip-before     Section title prefix.  Sections before the first occurrence
                    of a title containing this string are skipped (e.g. "Traits"
                    skips the intro pages).  Case-insensitive.  Optional.

Output structure
----------------
  <out>/
    <trait_slug>/
      page_000.png   ← first page of this trait's section (0-based within chunk)
      page_001.png
      ...
    manifest.json    ← {trait_slug: {title, toc_page, page_range, n_pages}}

Notes
-----
- Page numbers in the manifest are 0-based PDF page indices.
- `toc_page` is the page listed in the PDF TOC; the actual rendered first page
  may differ by one if LaTeX inserts a page break before the section.  The
  script uses the TOC page directly.
- If two traits share a figure (e.g. Figure 5 appears after both Face shaping
  and Lateral trimming), that figure appears in both trait directories.
- The `--skip-before` option is useful to exclude the intro/definitions pages,
  which are level-1 sections and would otherwise appear in the output if
  section-level is set to 1.
"""

import argparse
import json
import re
import sys
from pathlib import Path

import fitz  # PyMuPDF


# ── Helpers ───────────────────────────────────────────────────────────────────

def _slugify(title: str) -> str:
    """Convert a section title to a filesystem-safe slug."""
    slug = title.lower()
    slug = re.sub(r"[^a-z0-9]+", "_", slug)
    return slug.strip("_")


def _parse_toc(doc: fitz.Document, section_level: int) -> list[dict]:
    """Return TOC entries at the requested level.

    Each entry: {title, level, page (0-based)}
    """
    toc = doc.get_toc(simple=False)
    # fitz returns [level, title, page, dest] where page is 1-based
    entries = []
    for item in toc:
        level = item[0]
        title = item[1].strip()
        page  = item[2] - 1  # convert to 0-based
        entries.append({"level": level, "title": title, "page": max(0, page)})
    return [e for e in entries if e["level"] == section_level]


def _build_page_ranges(
    trait_entries: list[dict],
    n_pages: int,
    all_entries: list[dict],
) -> list[dict]:
    """For each trait entry, compute the page range [start, end) inclusive.

    The end of a trait's range is the page before the next entry of equal or
    higher (lower number) level in the full TOC, or the last page of the doc.
    """
    result = []
    for i, entry in enumerate(trait_entries):
        start = entry["page"]
        # Find the next TOC entry at any level <= entry["level"] after this one
        end = n_pages - 1
        for other in all_entries:
            if other["page"] > start:
                end = other["page"] - 1
                break
        result.append({
            "title":      entry["title"],
            "toc_page":   entry["page"],
            "page_start": start,
            "page_end":   end,
            "n_pages":    end - start + 1,
        })
    return result


# ── Main ──────────────────────────────────────────────────────────────────────

def decompose(
    pdf_path: Path,
    out_dir: Path,
    dpi: int = 150,
    section_level: int = 2,
    skip_before: str | None = None,
) -> dict:
    """Decompose a codebook PDF into per-trait page image directories.

    Returns the manifest dict.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    doc    = fitz.open(str(pdf_path))
    mat    = fitz.Matrix(dpi / 72, dpi / 72)
    n_pages = len(doc)

    print(f"Opened: {pdf_path.name}  ({n_pages} pages)")

    # Full TOC for end-of-range calculation
    all_toc = doc.get_toc(simple=False)
    all_entries = [
        {"level": item[0], "title": item[1].strip(), "page": max(0, item[2] - 1)}
        for item in all_toc
    ]

    trait_entries = [e for e in all_entries if e["level"] == section_level]

    if not trait_entries:
        print(f"ERROR: No TOC entries at level {section_level} found.  "
              f"Ensure the PDF was compiled with toc: true and section headings "
              f"at the correct depth.")
        sys.exit(1)

    print(f"Found {len(trait_entries)} level-{section_level} TOC entries.")

    # Apply skip_before filter
    if skip_before:
        skip_lower = skip_before.lower()
        # Find the first entry whose title contains skip_before
        first_match = next(
            (i for i, e in enumerate(trait_entries)
             if skip_lower in e["title"].lower()),
            None,
        )
        if first_match is not None:
            trait_entries = trait_entries[first_match:]
            print(f"  Skipping entries before section containing '{skip_before}' "
                  f"({first_match} entries skipped).")

    page_ranges = _build_page_ranges(trait_entries, n_pages, all_entries)

    manifest = {}

    for entry in page_ranges:
        title    = entry["title"]
        slug     = _slugify(title)
        start    = entry["page_start"]
        end      = entry["page_end"]

        trait_dir = out_dir / slug
        trait_dir.mkdir(exist_ok=True)

        print(f"  {slug}: pages {start}–{end} ({end - start + 1} pages)")

        for page_idx in range(start, end + 1):
            page = doc[page_idx]
            pix  = page.get_pixmap(matrix=mat)
            img_path = trait_dir / f"page_{page_idx - start:03d}.png"
            pix.save(str(img_path))

        manifest[slug] = {
            "title":      title,
            "toc_page":   entry["toc_page"],
            "page_start": start,
            "page_end":   end,
            "n_pages":    end - start + 1,
        }

    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"\nManifest saved to {manifest_path}")
    print(f"Decomposed {len(manifest)} trait sections into {out_dir}")

    return manifest


def main():
    parser = argparse.ArgumentParser(
        description="Decompose a codebook PDF into per-trait page image directories."
    )
    parser.add_argument("--pdf",  required=True, help="Path to compiled codebook PDF")
    parser.add_argument("--out",  required=True, help="Output directory")
    parser.add_argument("--dpi",  type=int, default=150,
                        help="Render DPI for page images (default: 150)")
    parser.add_argument("--section-level", type=int, default=2,
                        help="TOC level of trait headings (default: 2 for ## headings)")
    parser.add_argument("--skip-before", default=None,
                        help="Skip sections before the first one containing this "
                             "string (e.g. 'Traits' to skip intro pages). "
                             "Case-insensitive.")
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        print(f"ERROR: PDF not found: {pdf_path}")
        sys.exit(1)

    decompose(
        pdf_path      = pdf_path,
        out_dir       = Path(args.out),
        dpi           = args.dpi,
        section_level = args.section_level,
        skip_before   = args.skip_before,
    )


if __name__ == "__main__":
    main()