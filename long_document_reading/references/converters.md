# Converter reference for long_document_reading

Verification status, recorded 2026-11-07. The poppler tools below are verified present in the user's Muse environment at /usr/bin. None of the four named converters was installed in that environment on that date, so their entry points are recorded from their public documentation and are labeled untested here. Verify availability and the help output in the local environment before running any of them, and record the exact command used in the conversion record.

Update 2026-11-15: Docling has since been measured in use (a two-column journal article, where it returned the reference list in perfect sequence, as the skill body records), so treat Docling as verified for that measured case — a single two-column journal article (n=1), not as a general guarantee for the class. The other three converters remain untested here.

## Verified locally

- `pdfinfo <file>.pdf` for page count, page size, and metadata.
- `pdftotext -layout <file>.pdf <out>.txt` for plain text extraction that keeps line order. Use `-f N -l M` for a page range and `-` as the output name for standard output. Do not use `-layout` on a multi-column document: it joins the columns line by line, so there the default extraction (no `-layout`) is the one that reads the columns in sequence.
- `pdffonts <file>.pdf`, `pdfimages -list <file>.pdf`, and `pdfdetach -list <file>.pdf` for diagnosis.
- `pdftoppm -jpeg -r 150 -f N -l N <file>.pdf <prefix>` for rasterizing named pages.

## Untested here, entry points from public documentation

- Docling. Documented command line entry point `docling <file>.pdf`. Structure preserving output with headings and tables, the slowest of the group in published comparisons.
- PyMuPDF4LLM. A Python library used through `pymupdf4llm.to_markdown("<file>.pdf")`. Fast on born digital PDFs. AGPL license terms apply.
- Marker. Documented command line entry point `marker_single <file>.pdf`. OCR capable, strong on tables and scans, slow on CPU.
- MinerU. Documented command line entry point `mineru -p <file>.pdf`. OCR capable with strong table handling.
- MarkItDown. Documented command line entry point `markitdown <file>.pdf`. Lightweight across many formats, but on PDFs it does not recover heading structure and its speed varies sharply by document, including a stall on a roughly 100 page report in the user's own 2026-11-06 measurement.

## Selection notes

- Published benchmark rankings never choose the converter for a given document. The pilot in the skill body does, with its time budget.
- A converter that stalls on the pilot is a result, not a problem to wait out. Record it and switch.
