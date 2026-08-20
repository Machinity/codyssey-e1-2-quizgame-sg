"""나만의 퀴즈 게임 (터미널에서 동작하는 콘솔 프로그램)

- Quiz     : 퀴즈 한 문제를 표현한다.
- Storage  : state.json 파일을 읽고 쓴다.
- QuizGame : 메뉴, 게임 진행, 입력 처리 등 게임 전체를 관리한다.
"""

import json
import os
import random

# 데이터 파일은 프로젝트 루트(main.py와 같은 위치)의 state.json 을 사용한다.
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'state.json')


class Storage:
    """state.json 파일 저장/불러오기를 담당하는 클래스"""

    def __init__(self, path):
        self.path = path

    def load(self):
        """파일을 읽어 딕셔너리를 돌려준다. 없거나 손상되면 None을 돌려준다."""
        try:
            with open(self.path, 'r', encoding='utf-8') as file:
                data = json.load(file)
        except FileNotFoundError:
            print('저장된 데이터가 없어 기본 퀴즈로 시작합니다.')
            return None
        except (json.JSONDecodeError, UnicodeDecodeError):
            print('데이터 파일이 손상되어 기본 퀴즈로 복구합니다.')
            return None
        except OSError as error:
            print('데이터 파일을 읽지 못했습니다. (%s)' % error)
            return None

        if not isinstance(data, dict) or not isinstance(data.get('quizzes'), list):
            print('데이터 형식이 올바르지 않아 기본 퀴즈로 복구합니다.')
            return None
        return data

    def save(self, data):
        """딕셔너리를 UTF-8 JSON 파일로 저장한다."""
        try:
            with open(self.path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
            return True
        except OSError as error:
            print('저장에 실패했습니다. (%s)' % error)
            return False


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

    def __init__(self, storage):
            self.storage = storage
            self.quizzes = []       # Quiz 객체 목록
            self.best_score = 0     # 최고 점수 (100점 만점)
            self.best_correct = 0   # 최고 점수를 받았을 때 맞힌 문제 수
            self.best_total = 0     # 최고 점수를 받았을 때 푼 문제 수

    # ------------------------------------------------------------------
    # 기본 데이터 / 파일 입출력
    # ------------------------------------------------------------------
    def default_quizzes(self):
        """파일이 없거나 손상되었을 때 사용할 기본 퀴즈 (주제: 파이썬 기초)"""
        return [
            Quiz('파이썬에서 정수를 나타내는 자료형은?',
                 ['int', 'str', 'bool', 'list'], 1),
            Quiz('리스트를 만들 때 사용하는 괄호는?',
                 ['(소괄호)', '[대괄호]', '{중괄호}', '<꺾쇠괄호>'], 2),
            Quiz('참(True)과 거짓(False) 두 값만 가지는 자료형은?',
                 ['int', 'float', 'bool', 'str'], 3),
            Quiz('객체가 만들어질 때 자동으로 호출되는 메서드는?',
                 ['__str__', '__init__', '__main__', '__call__'], 2),
            Quiz('딕셔너리에서 값을 꺼낼 때 기준이 되는 것은?',
                 ['인덱스 번호', '키(key)', '슬라이스', '정규식'], 2),
            Quiz('오류가 발생해도 프로그램을 계속 실행하려면 무엇을 쓰는가?',
                 ['for / else', 'try / except', 'def / return', 'with / as'], 2),
        ]

    def build_quiz(self, item):
            """저장된 딕셔너리 하나를 Quiz 객체로 바꾼다. 형식이 틀리면 None."""
            if not isinstance(item, dict):
                return None
            question = item.get('question')
            choices = item.get('choices')
            answer = item.get('answer')
            if not isinstance(question, str) or question.strip() == '':
                return None
            if not isinstance(choices, list) or len(choices) != 4:
                return None
            if not isinstance(answer, int) or answer < 1 or answer > 4:
                return None
            return Quiz(question, choices, answer)

    def read_int(self, value):
            """저장된 값이 정수가 아니면 0으로 처리한다."""
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                return 0
            return value

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
        """저장된 퀴즈를 무작위 순서로 출제하고 결과를 보여준다."""
        if len(self.quizzes) == 0:
            print('등록된 퀴즈가 없습니다. 먼저 퀴즈를 추가해 주세요.')
            return

        order = self.shuffled_quizzes()
        total = len(order)
        correct = 0
        print()
        print('퀴즈를 시작합니다! (총 %d문제, 순서는 무작위입니다)' % total)
        print()

        for index in range(total):
            quiz = order[index]
            quiz.show(index + 1)
            picked = self.ask_number('정답 입력 (1-4): ', 1, 4)
            if quiz.is_correct(picked):
                correct = correct + 1
                print('정답입니다!')
            else:
                print('오답입니다. 정답은 %d번 (%s) 입니다.'
                        % (quiz.answer, quiz.answer_text()))
            print()

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
