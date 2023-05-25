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
            case "경제" | "기업" | "투자" | "시장" | "수입" | "수출" | "고용" | "업체":
                self.economic = True
            case "교육" | "학교":
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
            case "아동":
                self.child_related = True
            case "보건" | "코로나" | "코로나19" | "질병" | "병원" | "메르스":
                self.healthcare = True
            case "가족" | "주민" | "공공":
                self.social_welfare = True
            case "법안" | "법률" | "법적":
                self.legal = True
            case "보도" | "언론":
                self.media = True
            case "행정" | "부처" | "예산" | "지역" | "지방" | "국정" | "출신" | "공무원" | "여야":
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
