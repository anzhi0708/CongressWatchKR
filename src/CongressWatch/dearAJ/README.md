<div align="center">

  <img src="https://raw.githubusercontent.com/anzhi0708/dearAJ/main/img/logo.png" />

</div>

<br>

<div align="center">

  [![last-commit](https://img.shields.io/github/last-commit/anzhi0708/dearAJ?style=social)](https://github.com/anzhi0708/dearAJ/commits/main)    [![pypi-version](https://img.shields.io/pypi/v/dearaj?color=blue&style=flat-square)](https://pypi.org/project/dearaj) ![license](https://img.shields.io/github/license/anzhi0708/dearAJ?color=blue&style=flat-square)    ![repo-size](https://img.shields.io/github/repo-size/anzhi0708/dearAJ?style=social) ![release](https://img.shields.io/github/v/release/anzhi0708/dearAJ?style=flat-square) ![code-size](https://img.shields.io/github/languages/code-size/anzhi0708/dearAJ?style=flat-square)

</div>


# dearaj

**Data analysis tool for Korean National Assembly**

- [Usage](https://github.com/anzhi0708/dearAJ#usage)
	- [PDFText](https://github.com/anzhi0708/dearAJ#pdftext)
  - [MP](https://github.com/anzhi0708/dearAJ#assembly)
  - [Assembly](https://github.com/anzhi0708/dearAJ#assembly)
  - [Speak](https://github.com/anzhi0708/dearAJ#speak)
  - [Movie](https://github.com/anzhi0708/dearAJ#movie)
  - [Conference](https://github.com/anzhi0708/dearAJ#conferences)
  - [Conferences](https://github.com/anzhi0708/dearAJ#conferences)
  - [period](https://github.com/anzhi0708/dearAJ#period)
- [Notice](https://github.com/anzhi0708/dearAJ#notice)
- [License](https://github.com/anzhi0708/dearAJ#license)

## Features

- Built-in datasets from [국회영상회의록](https://w3.assembly.go.kr/main/index.do) and [열린국회정보](https://open.assembly.go.kr/portal/mainPage.do)
- Automatic data preprocessing that removes duplicated conference records from 국회영상회의록 website
- Crawlers from module `ajcore` to get up-to-date conference info at anytime


## Usage

```python
from dearaj import *
```

### period

An iterable collection of class `Conference`s, works like Python's built-in class `range`.

```python
>>> period("2019-01-01", "2019-03-01")
<class 'period', 10 conferences from 2019-01-01 to 2019-03-01>
```

- Checking each conference during a specific period of time.

```python
>>> for conf in period("2020-01-01", "2020-01-15"):
...     print(conf)
...
Conference(2020-01-09, 19:05, 목, 제374회 국회(임시회) 제02차 본회의, 1 movie(s))
Conference(2020-01-13, 18:34, 월, 제375회 국회(임시회) 제01차 본회의, 1 movie(s))
Conference(2020-01-07, 10:01, 화, 제374회 국회(임시회) 제03차 국무총리(정세균)임명동의에관한인사청문특별위원회, 4 movie(s))
Conference(2020-01-08, 10:00, 수, 제374회 국회(임시회) 제04차 국무총리(정세균)임명동의에관한인사청문특별위원회, 6 movie(s))
Conference(2020-01-09, 10:15, 목, 제374회 국회(임시회) 제01차 외교통일위원회, 1 movie(s))
Conference(2020-01-10, 10:06, 금, 제374회 국회(임시회) 제03차 법제사법위원회, 1 movie(s))
Conference(2020-01-03, 17:17, 금, 제374회 국회(임시회) 제02차 국무총리(정세균)임명동의에관한인사청문특별위원회, 1 movie(s))
Conference(2020-01-09, 10:37, 목, 제374회 국회(임시회) 제02차 법제사법위원회, 1 movie(s))
```

- Downloading each element's `.pdf` binary data.

```python
for conf in period("2019-01-01", "2019-12-31"):
		# Save as:
		file = f"{conf.date}_{conf.ct1}.{conf.ct2}.{conf.ct3}.{conf.mc}.pdf"
		with open(file, 'wb') as output:
				# Saving to local disk:
				output.write(conf.pdf)
```

### Assembly

Collection of single `MP`s using data from [열린국회정보](https://open.assembly.go.kr/portal/assm/search/memberHistSchPage.do).

- Checking if the 19th generation of assembly has a MP with the name of...

```python
>>> Assembly(19).has("문재인")
True
>>> Assembly(19).has("박근혜")
True
>>> Assembly(20).has("박근혜")
False
```

- Getting description...
```python
>>> Assembly(20)  # The 20th National Assembly of Korea
MPList(male=267, female=53, total=320)
```
```python
>>> for mp in Assembly(19):  # for each MP of the 19th Natioinal Assembly, search for
...     if mp.name == '문재인':  # the 12th president of Korea
...             print(mp)
...
MP(generation=19, name='문재인', party='민주통합당', committee=[], region='부산 사상구', gender='남', n='초선', how='지역구')
```

### PDFText

```python
>>> PDFText
<class 'ajpdf.PDFText'>
```

`PDFText` is a wrapper class based on module `PyMuPDF`; **it can parse a 국회호의록 PDF file into a Python `dict` in the form of `MP_NAME: LIST_OF_LINES_OF_HIS_OR_HER_SPEECH`**. Use `help(PDFText)` for more information.

### Conferences

`Conferences(n)` is the collection of the `n`th assembly's conferences. `Conference`s are also elements of `Conferences`s.

```python
>>> for conf in Conferences(15):
...     print(conf)
...     print(conf.movies)
...     break
...
<1999-12-28, 12:00, 화, 제209회 국회(임시회) 제01차 본회의(1 movies)>
[Movie(real_time=None, play_time='03:23:49', speak_type='전체보기', no=435998, sublist=[Speak(real_time=None, play_time='00:03:45', speak_type='보고', no=115668, speak_title='개의, 의사국장 보고', wv=0), Speak(real_time=None, play_time='00:01:00', speak_type='인사', no=115669, speak_title='박재규 통일부장관 인사', wv=0), Speak(real_time=None, play_time='00:05:20', speak_type='발언', no=115670, speak_title='윤한도의원 5분 자유발언', wv=0), Speak(real_time=None, play_time='00:05:15', speak_type='발언', no=115671, speak_title='박광태의원 5분 자유발언', wv=0), Speak(real_time=None, play_time='00:03:21', speak_type='발언', no=115672, speak_title='국창근의원 신상발언', wv=0), Speak(real_time=None, play_time='00:02:24', speak_type='설명', no=115673, speak_title='1.제209회국회(임시회)회기결정의건, 2.정치개혁입법특별위원회구성결의안 이윤수의원 제안설명', wv=0), Speak(real_time=None, play_time='00:06:57', speak_type='보고', no=115674, speak_title='3.민영교도소등의설치·운영에관한법률안 외 3건 安商守의원 제안설명 및 심사보고', wv=0), Speak(real_time=None, play_time='00:03:07', speak_type='설명', no=115675, speak_title='7.참전군인등지원에관한법률개정법률안(대안) 김영선의원 제안설명', wv=0), Speak(real_time=None, play_time='00:03:44', speak_type='보고', no=115676, speak_title='8.지방재정법중개정법률안 외 1건 홍문종의원 심사보고', wv=0), Speak(real_time=None, play_time='00:05:18', speak_type='보고', no=115677, speak_title='10.민주화운동관련자명예회복및보상등에관한법률안(대안) 외 1건 유선호의원 제안설명 및 심사보고', wv=0), Speak(real_time=None, play_time='00:05:55', speak_type='보고', no=115678, speak_title='12.방송법안 외 3건 신기남의원 심사보고', wv=0), Speak(real_time=None, play_time='00:05:06', speak_type='설명', no=115679, speak_title='이상현의원 제12항 수정안에 대한 제안설명', wv=0), Speak(real_time=None, play_time='00:06:05', speak_type='토론', no=115680, speak_title='박성범의원 제12항 수정안 반대토론', wv=0), Speak(real_time=None, play_time='00:06:48', speak_type='토론', no=115681, speak_title='신기남의원 제12항 수정안 찬성토론', wv=0), Speak(real_time=None, play_time='00:04:21', speak_type='보고', no=115682, speak_title='제12항 수정안 표결(기립표결, 가결), 제13항∼제15항 의결(가결), 16.변리사법중개정법률안', wv=0), Speak(real_time=None, play_time='00:02:08', speak_type='보고', no=115683, speak_title='신영국의원 심사보고', wv=0), Speak(real_time=None, play_time='00:06:24', speak_type='설명', no=115684, speak_title='김칠환의원 제16항 수정안에 대한 제안설명', wv=0), Speak(real_time=None, play_time='00:07:50', speak_type='토론', no=115685, speak_title='김경재의원 제16항 수정안 반대토론', wv=0), Speak(real_time=None, play_time='00:04:35', speak_type='보고', no=115686, speak_title='제16항 수정안 표결(기립표결, 부결, 원안 가결), 17.지방교육재정교부금법중개정법률안(대안) 외 3건', wv=0), Speak(real_time=None, play_time='00:10:23', speak_type='설명', no=115687, speak_title='박범진의원 제안설명', wv=0), Speak(real_time=None, play_time='00:02:30', speak_type='보고', no=115688, speak_title='21.영재교육법안 외 4건 이재오의원 심사보고', wv=0), Speak(real_time=None, play_time='00:05:40', speak_type='보고', no=115689, speak_title='26.초·중등교육법중개정법률안 외 2건 安相洙의원 심사보고', wv=0), Speak(real_time=None, play_time='00:03:47', speak_type='보고', no=115690, speak_title='29.과학기술진흥법중개정법률안 외 1건 정호선의원 제안설명 및 심사보고', wv=0), Speak(real_time=None, play_time='00:08:35', speak_type='보고', no=115691, speak_title='31.수산업협동조합법중개정법률안 외 3건 김기춘의원 심사보고', wv=0), Speak(real_time=None, play_time='00:03:55', speak_type='설명', no=115692, speak_title='35.사회복지사업법중개정법률안(대안) 박시균의원 제안설명', wv=0), Speak(real_time=None, play_time='00:08:34', speak_type='보고', no=115693, speak_title='36.한국도로공사법중개정법률안 외 4건 김고성의원 심사보고', wv=0), Speak(real_time=None, play_time='00:07:43', speak_type='설명', no=115694, speak_title='41.개발제한구역의지정및관리에관한특별조치법안(대안) 외 1건 이국헌의원 제안설명', wv=0), Speak(real_time=None, play_time='00:07:51', speak_type='설명', no=115695, speak_title='43.도시계획법개정법률안 외 2건 조진형의원 제안설명', wv=0), Speak(real_time=None, play_time='00:03:26', speak_type='설명', no=115696, speak_title='46.도시개발법안 외 6건 이윤수의원 제안설명 및 심사보고', wv=0), Speak(real_time=None, play_time='00:06:52', speak_type='설명', no=115697, speak_title='53.자동차손해배상보장법중개정법률안 외 3건 이재창의원 제안설명 및 심사보고', wv=0), Speak(real_time=None, play_time='00:03:01', speak_type='보고', no=115698, speak_title='57.1999년도국정감사결과보고서채택의건(16건), 58.화성시설치에관한청원', wv=0), Speak(real_time=None, play_time='00:02:43', speak_type='보고', no=115699, speak_title='박신원의원 심사보고', wv=0), Speak(real_time=None, play_time='00:01:25', speak_type='기타', no=115700, speak_title='휴회의건', wv=0), Speak(real_time=None, play_time='00:05:27', speak_type='발언', no=115701, speak_title='신영국의원 5분 자유발언', wv=0), Speak(real_time=None, play_time='00:05:21', speak_type='발언', no=115702, speak_title='정세균의원 5분 자유발언', wv=0), Speak(real_time=None, play_time='00:05:26', speak_type='발언', no=115703, speak_title='김문수의원 5분 자유발언', wv=0), Speak(real_time=None, play_time='00:03:51', speak_type='발언', no=115704, speak_title='김민석의원 5분 자유발언', wv=0), Speak(real_time=None, play_time='00:05:29', speak_type='발언', no=115705, speak_title='이경재의원 5분 자유발언', wv=0), Speak(real_time=None, play_time='00:05:20', speak_type='발언', no=115706, speak_title='이상배의원 5분 자유발언', wv=0), Speak(real_time=None, play_time='00:05:45', speak_type='발언', no=115707, speak_title='김학원의원 의사진행발언', wv=0), Speak(real_time=None, play_time='00:01:18', speak_type='발언', no=115708, speak_title='박준규 국회의장 발언, 산회', wv=0)])]
```

### Movie

A `Movie` object contains multuple `Speak`s, and other meta info. Sometimes a single `Conference` has multuple `Movie`s.

```python
>>> for conf in Conferences(10):
...     for movie in conf:
...             for speak in movie:
...                     print(speak)
...     break
...
Speak(real_time=None, play_time='00:05:58', speak_type='보고', no=106739, speak_title='구범모의원', wv=0)
Speak(real_time=None, play_time='00:02:15', speak_type='인사', no=106740, speak_title='부총리겸경제기획원장관', wv=0)
Speak(real_time=None, play_time='00:04:31', speak_type='기타', no=106741, speak_title='위원장', wv=0)
```

<div align="center">

  <img src="https://raw.githubusercontent.com/anzhi0708/dearAJ/main/img/actual_kr_conf_site_page.png" />
  A 'Movie' object contains multiple 'Speak' objects.

</div>

### Speak

Info about some specific `MP`'s speech, such as `speak_type` etc. A `Movie` can hold multuple `Speak`s.

## Notice

**This module was designed for personal usage**; `README` file / `pip` package may be out-of-date. The best way to use this package is by `git clone`ing this repo; some of the features are not mentioned so you have to discover them on your own.

## License

Copyright Anji Wong, 2022.

Distributed under the terms of the Apache 2.0 license.
