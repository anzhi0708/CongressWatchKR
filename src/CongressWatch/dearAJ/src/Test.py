from dearaj import *
from unicodedata import normalize


# Generation: 20 + 21
P_START = "2019-01-01"
P_END = "2021-01-01"
TARGET_PERIOD = period(P_START, P_END)
TARGET_NAMES = []
TARGET_NAMES_NOT_NORMALIZED = []


def test_should_throw_error():
    """This should throw an error due to lack of argument"""
    MPSpeechRecord.get_by_period_and_name(start=P_START, end=P_END)


def test_basic():
    """Should have the same output"""
    for mp in Assembly(20):
        if mp in Assembly(21):
            if mp.is_female:
                TARGET_NAMES.append(normalize("NFKC", mp.name))
                TARGET_NAMES_NOT_NORMALIZED.append(mp.name)
    result = []
    for TARGET_NAME in TARGET_NAMES:
        result.append(get_mp_speech_record(start=P_START, end=P_END, name=TARGET_NAME))
    print(result)
    total = 0
    for r in result:
        total += r.size
    print(f"{total = }")
    total = 0
    for conf in TARGET_PERIOD:
        for name in TARGET_NAMES_NOT_NORMALIZED:
            if conf.has(name):
                total += 1
    print(total)


def test():
    names = []
    for mp in Assembly(20):
        if mp in Assembly(21):
            if mp.is_female:
                names.append(mp.name)
    result = []
    for name in names:
        result.append(get_mp_speech_record(start=P_START, end=P_END, name=name))
        break
    return result


result = test()[0].speeches
