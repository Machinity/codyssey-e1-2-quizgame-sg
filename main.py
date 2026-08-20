"""나만의 퀴즈 게임 (터미널에서 동작하는 콘솔 프로그램)

- Quiz     : 퀴즈 한 문제를 표현한다.
- Storage  : state.json 파일을 읽고 쓴다.
- QuizGame : 메뉴, 게임 진행, 입력 처리 등 게임 전체를 관리한다.
"""

import datetime
import json
import os
import random

# 데이터 파일은 프로젝트 루트(main.py와 같은 위치)의 state.json 을 사용한다.
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'state.json')

# 힌트를 한 번 볼 때마다 최종 점수에서 깎는 점수
HINT_PENALTY = 10


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

    def __init__(self, question, choices, answer, hint=''):
        self.question = question    # 문제 (str)
        self.choices = choices      # 선택지 4개 (list)
        self.answer = answer        # 정답 번호 1~4 (int)
        self.hint = hint            # 힌트 (str, 없으면 빈 문자열)

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

    def has_hint(self):
        """힌트가 등록되어 있으면 True를 돌려준다."""
        return self.hint.strip() != ''

    def show_hint(self):
        """힌트를 출력한다. 힌트가 있으면 True, 없으면 False를 돌려준다."""
        if not self.has_hint():
            print('이 문제에는 힌트가 없습니다.')
            return False
        print('힌트: %s (점수 %d점 차감)' % (self.hint, HINT_PENALTY))
        return True

    def to_dict(self):
        """JSON으로 저장하기 위해 딕셔너리로 바꾼다."""
        return {
            'question': self.question,
            'choices': self.choices,
            'answer': self.answer,
            'hint': self.hint,
        }

    
class QuizGame:
    """게임 전체를 관리하는 클래스"""

    def __init__(self, storage):
        self.storage = storage
        self.quizzes = []       # Quiz 객체 목록
        self.best_score = 0     # 최고 점수 (100점 만점)
        self.best_correct = 0   # 최고 점수를 받았을 때 맞힌 문제 수
        self.best_total = 0     # 최고 점수를 받았을 때 푼 문제 수
        self.history = []       # 게임 기록 목록 (딕셔너리들의 리스트)

    # ------------------------------------------------------------------
    # 기본 데이터 / 파일 입출력
    # ------------------------------------------------------------------
    def default_quizzes(self):
        """파일이 없거나 손상되었을 때 사용할 기본 퀴즈 (주제: 파이썬 기초)"""
        return [
            Quiz('파이썬에서 정수를 나타내는 자료형은?',
                 ['int', 'str', 'bool', 'list'], 1,
                 'integer(정수)를 줄인 이름입니다.'),
            Quiz('리스트를 만들 때 사용하는 괄호는?',
                 ['(소괄호)', '[대괄호]', '{중괄호}', '<꺾쇠괄호>'], 2,
                 '딕셔너리는 { }, 튜플은 ( ) 를 사용합니다.'),
            Quiz('참(True)과 거짓(False) 두 값만 가지는 자료형은?',
                 ['int', 'float', 'bool', 'str'], 3,
                 '논리학자 George Boole 의 이름에서 온 자료형입니다.'),
            Quiz('객체가 만들어질 때 자동으로 호출되는 메서드는?',
                 ['__str__', '__init__', '__main__', '__call__'], 2,
                 '이름 안에 initialize(초기화)의 앞부분이 들어 있습니다.'),
            Quiz('딕셔너리에서 값을 꺼낼 때 기준이 되는 것은?',
                 ['인덱스 번호', '키(key)', '슬라이스', '정규식'], 2,
                 '{ 이름: 값 } 형태로 저장하고, 그 이름으로 값을 찾습니다.'),
            Quiz('오류가 발생해도 프로그램을 계속 실행하려면 무엇을 쓰는가?',
                 ['for / else', 'try / except', 'def / return', 'with / as'], 2,
                 '오류를 잡아서(catch) 처리하는 문법입니다.'),
        ]

    def build_quiz(self, item):
        """저장된 딕셔너리 하나를 Quiz 객체로 바꾼다. 형식이 틀리면 None."""
        if not isinstance(item, dict):
            return None
        question = item.get('question')
        choices = item.get('choices')
        answer = item.get('answer')
        hint = item.get('hint')
        if not isinstance(question, str) or question.strip() == '':
            return None
        if not isinstance(choices, list) or len(choices) != 4:
            return None
        if not isinstance(answer, int) or answer < 1 or answer > 4:
            return None
        if not isinstance(hint, str):
            hint = ''       # 힌트는 없어도 되므로 형식이 틀리면 빈 값으로 둔다.
        return Quiz(question, choices, answer, hint)

    def build_record(self, item):
        """저장된 게임 기록 하나를 확인한다. 형식이 틀리면 None."""
        if not isinstance(item, dict):
            return None
        date = item.get('date')
        if not isinstance(date, str):
            return None
        return {
            'date': date,
            'total': self.read_int(item.get('total')),
            'correct': self.read_int(item.get('correct')),
            'score': self.read_int(item.get('score')),
        }

    def load(self):
        """state.json에서 퀴즈와 최고 점수, 게임 기록을 불러온다."""
        data = self.storage.load()
        if data is None:
            self.quizzes = self.default_quizzes()
            self.save()
            return

        quizzes = []
        for item in data.get('quizzes', []):
            quiz = self.build_quiz(item)
            if quiz is not None:
                quizzes.append(quiz)

        if len(quizzes) == 0:
            print('사용할 수 있는 퀴즈가 없어 기본 퀴즈로 복구합니다.')
            quizzes = self.default_quizzes()

        self.quizzes = quizzes
        self.best_score = self.read_int(data.get('best_score'))
        self.best_correct = self.read_int(data.get('best_correct'))
        self.best_total = self.read_int(data.get('best_total'))

        records = []
        raw_history = data.get('history')
        if isinstance(raw_history, list):
            for item in raw_history:
                record = self.build_record(item)
                if record is not None:
                    records.append(record)
        self.history = records
        print('저장된 데이터를 불러왔습니다. (퀴즈 %d개, 최고점수 %d점)'
              % (len(self.quizzes), self.best_score))

    def read_int(self, value):
            """저장된 값이 정수가 아니면 0으로 처리한다."""
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                return 0
            return value

    def save(self):
        """현재 퀴즈와 최고 점수를 state.json에 저장한다."""
        quiz_list = []
        for quiz in self.quizzes:
            quiz_list.append(quiz.to_dict())
        data = {
            'quizzes': quiz_list,
            'best_score': self.best_score,
            'best_correct': self.best_correct,
            'best_total': self.best_total,
            'history': self.history,
        }
        return self.storage.save(data)

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

    def ask_optional_text(self, message):
        """입력하지 않고 Enter만 눌러도 되는 값을 입력받는다. (힌트용)"""
        return input(message).strip()

    def ask_answer(self, quiz):
        """정답 번호를 입력받는다. 0을 입력하면 힌트를 보여주고 다시 물어본다.

        돌려주는 값은 (고른 번호, 힌트를 썼는지 여부) 두 개다.
        0은 정답으로 인정되지 않으므로, 정답으로 받는 값은 항상 1~4 이다.
        """
        used_hint = False
        while True:
            picked = self.ask_number('정답 입력 (1-4, 힌트 보기는 0): ', 0, 4)
            if picked == 0:
                if quiz.show_hint():
                    used_hint = True    # 힌트를 여러 번 봐도 차감은 한 번만 한다.
                continue
            return picked, used_hint

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
        print('3. 퀴즈 삭제')
        print('4. 퀴즈 목록')
        print('5. 점수 확인')
        print('6. 기록 보기')
        print('7. 종료')
        print('========================================')

    def shuffled_quizzes(self):
        """퀴즈 목록을 복사한 뒤 순서를 무작위로 섞어서 돌려준다.

        self.quizzes 를 직접 섞으면 저장 순서까지 바뀌므로,
        list()로 복사본을 만들어 그 복사본만 섞는다.
        """
        order = list(self.quizzes)
        random.shuffle(order)
        return order

    def ask_count(self, limit):
        """몇 문제를 풀지 입력받는다. 퀴즈가 1개뿐이면 묻지 않는다."""
        if limit == 1:
            return 1
        print()
        print('등록된 퀴즈는 총 %d개입니다.' % limit)
        return self.ask_number('몇 문제를 풀까요? (1-%d): ' % limit, 1, limit)

    def play(self):
        """저장된 퀴즈를 무작위 순서로 출제하고 결과를 보여준다."""
        if len(self.quizzes) == 0:
            print('등록된 퀴즈가 없습니다. 먼저 퀴즈를 추가해 주세요.')
            return

        shuffled = self.shuffled_quizzes()
        total = self.ask_count(len(shuffled))
        order = shuffled[0:total]     # 섞인 목록에서 앞에서부터 total개만 사용한다.
        correct = 0
        hint_count = 0
        print()
        print('퀴즈를 시작합니다! (총 %d문제, 순서는 무작위입니다)' % total)
        print('힌트가 필요하면 0을 입력하세요. (힌트 1회당 %d점 차감)' % HINT_PENALTY)
        print()

        for index in range(total):
            quiz = order[index]
            quiz.show(index + 1)
            picked, used_hint = self.ask_answer(quiz)
            if used_hint:
                hint_count = hint_count + 1
            if quiz.is_correct(picked):
                correct = correct + 1
                print('정답입니다!')
            else:
                print('오답입니다. 정답은 %d번 (%s) 입니다.'
                        % (quiz.answer, quiz.answer_text()))
            print()

        score = int(correct * 100) - hint_count * HINT_PENALTY
        if score < 0:
            score = 0       # 아무리 많이 깎여도 0점 아래로는 내려가지 않는다.
        print('========================================')
        print('결과: %d문제 중 %d문제 정답! (%d점)' % (total, correct, score))
        if hint_count > 0:
            print('힌트 %d번 사용으로 %d점이 차감되었습니다.'
                  % (hint_count, hint_count * HINT_PENALTY))
        if score > self.best_score:
            self.best_score = score
            self.best_correct = correct
            self.best_total = total
            print('새로운 최고 점수입니다!')
        else:
            print('현재 최고 점수는 %d점입니다.' % self.best_score)
        print('========================================')
        self.add_history(total, correct, score)
        self.save() 

    def add_quiz(self):
        """새 퀴즈를 입력받아 목록에 넣고 파일에 저장한다."""
        print()
        print('새로운 퀴즈를 추가합니다.')
        question = self.ask_text('문제를 입력하세요: ')
        choices = []
        for number in range(1, 5):
            choices.append(self.ask_text('선택지 %d: ' % number))
        answer = self.ask_number('정답 번호 (1-4): ', 1, 4)
        hint = self.ask_optional_text('힌트 (없으면 그냥 Enter): ')

        self.quizzes.append(Quiz(question, choices, answer, hint))
        if self.save():
            print('퀴즈가 추가되었습니다! (현재 %d개)' % len(self.quizzes))

    def delete_quiz(self):
        """번호를 골라 퀴즈를 지우고 파일에 반영한다."""
        if len(self.quizzes) == 0:
            print()
            print('등록된 퀴즈가 없어 삭제할 수 없습니다.')
            return

        self.show_list()
        count = len(self.quizzes)
        number = self.ask_number('삭제할 퀴즈 번호 (1-%d): ' % count, 1, count)
        target = self.quizzes[number - 1]
        print('선택한 퀴즈: %s' % target.question)
        confirm = self.ask_number('정말 삭제할까요? (1: 삭제, 2: 취소): ', 1, 2)
        if confirm == 2:
            print('삭제를 취소했습니다.')
            return

        self.quizzes.pop(number - 1)
        if self.save():
            print('퀴즈를 삭제했습니다. (현재 %d개)' % len(self.quizzes))

    def show_list(self):
        """등록된 퀴즈 목록을 보여준다."""
        print()
        if len(self.quizzes) == 0:
            print('등록된 퀴즈가 없습니다. 먼저 퀴즈를 추가해 주세요.')
            return

        print('등록된 퀴즈 목록 (총 %d개)' % len(self.quizzes))
        print('----------------------------------------')
        for index in range(len(self.quizzes)):
            print('[%d] %s' % (index + 1, self.quizzes[index].question))
        print('----------------------------------------')

    def add_history(self, total, correct, score):
        """한 판이 끝날 때마다 날짜/시간과 성적을 기록에 추가한다."""
        now = datetime.datetime.now()
        self.history.append({
            'date': now.strftime('%Y-%m-%d %H:%M:%S'),
            'total': total,
            'correct': correct,
            'score': score,
        })

    def show_history(self):
        """지금까지의 게임 기록을 최근 것부터 보여준다."""
        print()
        if len(self.history) == 0:
            print('아직 게임 기록이 없습니다. 먼저 퀴즈를 풀어 보세요.')
            return

        print('게임 기록 (총 %d번, 최근 10번까지 표시)' % len(self.history))
        print('----------------------------------------')
        start = len(self.history) - 10
        if start < 0:
            start = 0
        for index in range(len(self.history) - 1, start - 1, -1):
            record = self.history[index]
            print('[%d] %s | %d문제 중 %d문제 정답 | %d점'
                  % (index + 1, record['date'], record['total'],
                     record['correct'], record['score']))
        print('----------------------------------------')

    def show_score(self):
        """최고 점수를 보여준다."""
        print()
        if self.best_total == 0:
            print('아직 퀴즈를 풀지 않았습니다. 먼저 퀴즈를 풀어 보세요.')
            return
        print('최고 점수: %d점 (%d문제 중 %d문제 정답)'
              % (self.best_score, self.best_total, self.best_correct))

    def run(self):
        """프로그램의 전체 흐름을 담당한다."""
        self.load()
        while True:
            self.show_menu()
            choice = self.ask_number('선택: ', 1, 7)
            if choice == 1:
                self.play()
            elif choice == 2:
                self.add_quiz()
            elif choice == 3:
                self.delete_quiz()
            elif choice == 4:
                self.show_list()
            elif choice == 5:
                self.show_score()
            elif choice == 6:
                self.show_history()
            elif choice == 7:
                self.save()
                print('게임을 종료합니다.')
                return


def main():
    game = QuizGame(Storage(STATE_FILE))
    try:
        game.run()
    except (KeyboardInterrupt, EOFError):
        print()
        print('입력이 중단되어 프로그램을 종료합니다. 데이터를 저장합니다.')
        game.save()


if __name__ == '__main__':
    main()
