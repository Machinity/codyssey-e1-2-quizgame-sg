class QuizGame:
    """게임 전체를 관리하는 클래스"""


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
