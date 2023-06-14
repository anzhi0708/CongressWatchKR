class Word:
    def __init__(self, string: str):
        self.word: str = string
        self.economic = False
        self.women_related = False
        self.child_related = False
        self.educational = False
        self.military = False
        self.deplomatic = False
        self.environmental = False
        self.social_welfare = False
        self.healthcare = False
        self.legal = False
        self.media = False
        self.domestic = False

        match self.word:
            case "건강":
                self.social_welfare = True
                self.healthcare = True
            case "회사" | "경제" | "기업" | "투자" | "시장" | "수입" | "수출" | "고용" | "업체" | "일자리" | "은행":
                self.economic = True
            case "교육" | "학교" | "학생":
                self.educational = True
                self.child_related = True
            case "군대" | "군사" | "무기":
                self.military = True
            case "미국" | "중국" | "북한" | "일본" | "외교":
                self.deplomatic = True
            case "환경" | "오염":
                self.environmental = True
                self.social_welfare = True
            case "복지":
                self.social_welfare = True
            case "여성":
                self.women_related = True
            case "아동" | "학생":
                self.child_related = True
            case "보건" | "코로나" | "코로나19" | "질병" | "병원" | "메르스" | "방역":
                self.healthcare = True
            case "가족" | "주민" | "공공":
                self.social_welfare = True
            case "법안" | "법률" | "법적" | "법률안" | "불법":
                self.legal = True
            case "보도" | "언론":
                self.media = True
            case "행정" | "부처" | "예산" | "지역" | "지방" | "국정" | "출신" | "공무원" | "여야" | "야당" | "여당" | "의석" | "개발" | "발의" | "집행" | "지자체" | "심의" | "후보" | "국내":
                self.domestic = True
            case "개정":
                self.domestic = True
                self.legal = True
            case "재정" | "산업":
                self.economic = True
                self.domestic = True
            case "문화":
                self.educational = True


if __name__ == "__main__":
    word = Word("경제")
    from pprint import pp

    pp(word.__dict__)
