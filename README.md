# CongressWatch

A PDF parser / data analysis tool for Korean National Assembly.

It uses `PyMuPDF` to parse PDF files. The TUI application was built with `textual` package (0.11.1).

## Usage

```bash
# Download this repo
git clone https://github.com/anzhi0708/CongressWatchKR.git
cd CongressWatchKR/src/CongressWatch

# TUI mode
./app.py <KR_ASSEMBLY_PDF_FILE>

# CLI mode
./ajpdf.py <KR_ASSEMBLY_PDF_FILE>
```

## Notice

This package is basically a 국회회의록 PDF parser. You should probably use something like `dearAJ` (crawler) to download the PDF data first.
