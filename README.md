## Usage

- TUI Mode

```bash
./app.py PDF_FILE
```

Example:

```bash
./app.py pdf_for_testing/sample_2020.pdf
```

- CLI Mode
```bash
./ajpdf.py PDF_FILE
```

- With Python
```python
>>> import CongressWatch as cw
>>> cw.period("2019-01-01", "2019-03-01")
<'period' object, with 10 conferences from 2019-01-01 to 2019-03-01, at 0x10f159900>
>>> for conf in cw.period("2019-01-01", "2019-03-01"): print(conf)
...
Conference(2019-01-09, 14:05, 수, 제365회 국회(임시회) 제04차 남북경제협력특별위원회, 2 movie(s))
Conference(2019-01-01, 00:15, 화, 제365회 국회(임시회) 제02차 국회운영위원회, 1 movie(s))
Conference(2019-01-16, 09:36, 수, 제365회 국회(임시회) 폐회중 제01차 과학기술정보방송통신위원회, 1 movie(s))
Conference(2019-01-15, 10:16, 화, 제365회 국회(임시회) 제01차 국방위원회, 1 movie(s))
Conference(2019-01-09, 10:24, 수, 제365회 국회(임시회) 제02차 행정안전위원회, 1 movie(s))
Conference(2019-01-09, 11:05, 수, 제365회 국회(임시회) 제01차 보건복지위원회, 1 movie(s))
Conference(2019-01-18, 10:03, 금, 제365회 국회(임시회) 폐회중 제02차 보건복지위원회, 2 movie(s))
Conference(2019-01-22, 14:28, 화, 제366회 국회(임시회) 제01차 문화체육관광위원회, 1 movie(s))
Conference(2019-01-21, 14:38, 월, 제366회 국회(임시회) 제01차 행정안전위원회, 1 movie(s))
Conference(2019-01-24, 10:07, 목, 제366회 국회(임시회) 제08차 정치개혁특별위원회, 1 movie(s))
```

## Details

- `test.sh`: Used to find missing job titles / PDF data misspells.
- `ajconsole.py`: A simple module which is basically useless and not necessary.
- `ajpdf.py`: Wrapper around `PyMuPDF` with extra functionalities for parsing KR National Assemb PDF data.
- `bin/`: I used `Nuitka` to compile Python scripts to native code for speed.
- `images/`: Some bugs captured during testing, some screenshots.
- `log/`: Basically for debugging.
- Other files or directories: Fairly easy to understand by their names / contents.
