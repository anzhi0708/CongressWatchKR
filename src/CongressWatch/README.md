## Usage

- TUI Mode

```bash
./app.py [PDF_FILE]
```

Example:

```bash
./app.py pdf_for_testing/sample_2020.pdf
```

- CLI Mode
```bash
./ajpdf.py [PDF_FILE]
```

## Details

- `test.sh`: Used to find missing job titles / PDF data misspells.
- `ajconsole.py`: A simple module which is basically useless and not necessary.
- `ajpdf.py`: Wrapper around `PyMuPDF` with extra functionalities for parsing KR National Assemb PDF data.
- `bin/`: I used `Nuitka` to compile Python scripts to native code for speed.
- `images/`: Some bugs captured during testing, some screenshots.
- `log/`: Basically for debugging.
- Other files or directories: Fairly easy to understand by their names / contents.
