# CongressWatch

Wrapper around `PyMuPDF` with extra functionalities for parsing KR National Assemb PDF data.

## Usage

- TUI Mode

```bash
./app.py <PDF_FILE>
```

Example:

```bash
./app.py pdf_for_testing/sample_2020.pdf
```

- CLI Mode
```bash
./ajpdf.py <PDF_FILE>
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

Downloading PDF files

```python

>>> import CongressWatch as cw
>>> for conf in cw.period("2019-01-01", "2019-03-01"):
...     file = f"{conf.date}_{conf.ct1}.{conf.ct2}.{conf.ct3}.{conf.mc}.pdf"
...     with open(f"./{file}", 'wb') as out:
...             out.write(conf.pdf)
...

1760256
498688
1280000
486400
494592
1103872
1641472
412672
475136
714752
```
```bash
2019-01-01_20.365.02.324.pdf  2019-01-18_20.365.02.333.pdf
2019-01-09_20.365.01.333.pdf  2019-01-21_20.366.01.345.pdf
2019-01-09_20.365.02.345.pdf  2019-01-22_20.366.01.359.pdf
2019-01-09_20.365.04.4GT.pdf  2019-01-24_20.366.08.4AL.pdf
2019-01-15_20.365.01.337.pdf  CongressWatch/
2019-01-16_20.365.01.356.pdf
```

Getting the MP list of a specific period

```python
>>> import CongressWatch as cw
>>> cw.Assembly(19).has("문재인")
True
>>> cw.Assembly(20).has("박근혜")
False

```

`PDFText` is a wrapper class based on the `PyMuPDF` module. It can parse a 국회호의록 PDF file into a **Python dictionary** in the form of *MP_NAME: LIST_OF_LINES_OF_HIS_OR_HER_SPEECH*. For more information, use the built-in function `help`.

```python
>>> cw.PDFText
<class 'ajpdf.PDFText'>
```

`Conferences(N)` is a collection of conferences for the nth assembly. `Conferences` contain elements of `Conference`s.

```python
>>> for conf in cw.Conferences(15):
...     print(conf)
...     print(conf.movies)
...     break
...
Conference(1999-12-28, 12:00, 화, 제209회 국회(임시회) 제01차 본회의, 1 movie(s))
[Movie(41 speak(s))]
```

`Movie` objects

```python
for conf in cw.Conferences(10):
...     for movie in conf:
...             for speak in movie:
...                     print(speak)
...     break
...
Speak(real_time=None, play_time='00:05:58', speak_type='보고', no=106739, speak_title='구범모의원', wv=0)
Speak(real_time=None, play_time='00:02:15', speak_type='인사', no=106740, speak_title='부총리겸경제기획원장관', wv=0)
Speak(real_time=None, play_time='00:04:31', speak_type='기타', no=106741, speak_title='위원장', wv=0)

```

## Note

This was designed for personal usage; the latest version is currently not available with `pip install`. If you want to use it, consider `git clone` it.

