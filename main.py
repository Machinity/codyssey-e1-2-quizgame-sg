class Quiz:
    """퀴즈 한 문제를 표현하는 클래스"""

    def __init__(self, question, choices, answer):
        self.question = question    # 문제 (str)
        self.choices = choices      # 선택지 4개 (list)
        self.answer = answer        # 정답 번호 1~4 (int)

    def show(self, number):
        """문제와 선택지를 화면에 출력한다."""
        print('----------------------------------------')
        print('[문제 %d] %s' % (number, self.question))
        print()
        for index in range(len(self.choices)):
            print('  %d. %s' % (index + 1, self.choices[index]))
        print()

    def is_correct(self, picked):
        """사용자가 고른 번호가 정답이면 True를 돌려준다."""
        return picked == self.answer

    def answer_text(self):
        """정답 선택지의 내용을 돌려준다."""
        return self.choices[self.answer - 1]

    def to_dict(self):
        """JSON으로 저장하기 위해 딕셔너리로 바꾼다."""
        return {
            'question': self.question,
            'choices': self.choices,
            'answer': self.answer,
        }

    
class QuizGame:
    """게임 전체를 관리하는 클래스"""

    # ------------------------------------------------------------------
    # 입력 처리
    # ------------------------------------------------------------------
    def ask_text(self, message):
        """빈 값이 아닌 문자열을 입력받는다."""
        while True:
            text = input(message).strip()
            if text == '':
                print('입력이 비어 있습니다. 다시 입력해 주세요.')
                continue
            return text

    def ask_number(self, message, low, high):
        """low~high 사이의 숫자를 입력받는다. 잘못된 입력은 다시 물어본다."""
        while True:
            text = input(message).strip()
            if text == '':
                print('입력이 비어 있습니다. %d-%d 사이의 숫자를 입력하세요.' % (low, high))
                continue
            try:
                number = int(text)
            except ValueError:
                print('잘못된 입력입니다. %d-%d 사이의 숫자를 입력하세요.' % (low, high))
                continue
            if number < low or number > high:
                print('잘못된 입력입니다. %d-%d 사이의 숫자를 입력하세요.' % (low, high))
                continue
            return number

    # ------------------------------------------------------------------
    # 메뉴 기능
    # ------------------------------------------------------------------
    def show_menu(self):
            print()
            print('========================================')
            print('           나만의 퀴즈 게임')
            print('========================================')
            print('1. 퀴즈 풀기')
            print('2. 퀴즈 추가')
            print('3. 퀴즈 목록')
            print('4. 점수 확인')
            print('5. 종료')
            print('========================================')

    def play(self):
        pass

    def add_quiz(self):
            pass

    def show_list(self):
            pass

    def show_score(self):
            pass

    def save(self):
            pass

    def run(self):
        """프로그램의 전체 흐름을 담당한다."""
        self.load()
        while True:
            self.show_menu()
            choice = self.ask_number('선택: ', 1, 5)
            if choice == 1:
                self.play()
            elif choice == 2:
                self.add_quiz()
            elif choice == 3:
                self.show_list()
            elif choice == 4:
                self.show_score()
            elif choice == 5:
                self.save()
                print('게임을 종료합니다. 안녕히 가세요!')
                return


def main():
    game = QuizGame()
    try:
        game.run()
    except (KeyboardInterrupt, EOFError):
        print()
        print('입력이 중단되어 프로그램을 종료합니다. 데이터를 저장합니다.')
        game.save()


if __name__ == '__main__':
    main()
