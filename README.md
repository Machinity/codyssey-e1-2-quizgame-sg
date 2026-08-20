# codyssey-e1-2-quizgame-sg

## 1. 프로젝트 개요

터미널에서 동작하는 콘솔 퀴즈 게임입니다.
메뉴에서 번호를 선택해 **퀴즈 풀기 / 추가 / 삭제 / 목록 / 점수 확인 / 기록 보기** 기능을 사용할 수 있습니다.

퀴즈와 최고 점수, 게임 기록은 `state.json` 파일에 저장되기 때문에,
프로그램을 껐다가 다시 켜도 내가 추가한 퀴즈와 점수가 그대로 유지됩니다.

- 사용 언어: Python 3.10 이상
- 외부 라이브러리 없음 (표준 라이브러리 `json`, `os`, `random`, `datetime` 만 사용)

## 2. 퀴즈 주제와 선정 이유

**주제: 파이썬 기초 문법**

이번 미션에서 파이썬 기본 개념을
그대로 문제로 만들었습니다.

- 정답이 명확해서 4지선다 형식으로 만들기에 적합한 주제였습니다.

## 3. 실행 방법

```bash
git clone https://github.com/Machinity/codyssey-e1-2-quizgame-sg.git
cd codyssey-e1-2-quizgame-sg
python3 main.py
```

이미 저장소를 내려받았다면 파일이 있는 경로에서 아래 명령만 실행하면 됩니다.

```bash
python3 main.py
```

실행하면 메뉴가 출력되고, 원하는 기능의 번호(1~7)를 입력하면 됩니다.

## 4. 기능 목록

| 번호 | 기능 | 설명 |
| --- | --- | --- |
| 1 | 퀴즈 풀기 | 몇 문제를 풀지 고르면, 저장된 퀴즈를 무작위 순서로 출제합니다. 정답/오답을 알려주고 최종 점수를 계산하며, 최고 점수를 넘으면 갱신해 저장합니다. |
| 2 | 퀴즈 추가 | 문제, 선택지 4개, 정답 번호, 힌트(선택)를 입력받아 새 퀴즈를 만들고 저장합니다. |
| 3 | 퀴즈 삭제 | 목록에서 번호를 골라 퀴즈를 삭제합니다. 삭제 전에 한 번 더 확인하고, 삭제 결과를 파일에 반영합니다. |
| 4 | 퀴즈 목록 | 등록된 퀴즈의 문제 목록을 번호와 함께 출력합니다. |
| 5 | 점수 확인 | 최고 점수와 그때의 성적(몇 문제 중 몇 문제 정답)을 보여줍니다. |
| 6 | 기록 보기 | 지금까지 플레이한 모든 게임의 날짜/시간, 푼 문제 수, 정답 수, 점수를 최근 순으로 보여줍니다. (최근 10번 표시) |
| 7 | 종료 | 데이터를 저장하고 프로그램을 끝냅니다. |

### 보너스 기능

| 보너스 | 구현 내용 |
| --- | --- |
| 랜덤 출제 | `random.shuffle()`로 문제 순서를 매번 섞습니다. `self.quizzes`를 직접 섞으면 `state.json`의 저장 순서까지 바뀌므로, `list()`로 복사본을 만들어 복사본만 섞습니다. (`shuffled_quizzes()`) |
| 문제 수 선택 | 퀴즈 풀기를 고르면 "몇 문제를 풀까요?"를 먼저 물어보고, 섞인 목록에서 앞에서부터 그 개수만 출제합니다. (`ask_count()`) |
| 힌트 기능 | `Quiz`에 `hint` 속성을 두고, 정답 입력 중 `0`을 누르면 힌트를 보여줍니다. 힌트 1회당 최종 점수에서 5점(`HINT_PENALTY`)을 깎으며, 같은 문제에서 힌트를 여러 번 봐도 차감은 한 번만 합니다. 점수는 0점 아래로 내려가지 않습니다. |
| 퀴즈 삭제 | 메뉴 3번에서 번호로 퀴즈를 지우고 바로 파일에 저장합니다. (`delete_quiz()`) |
| 기록 히스토리 | 한 판이 끝날 때마다 `datetime`으로 날짜/시간을 남겨 `history`에 기록하고, 메뉴 6번에서 확인합니다. (`add_history()`, `show_history()`) |

### 예외 처리

- 숫자를 입력해야 하는 곳에서 앞뒤 공백을 제거한 뒤 처리합니다. (예: ` 1 ` → `1`)
- 숫자가 아닌 값(`abc`), 범위 밖의 숫자(`9`), 빈 입력(그냥 Enter)은 안내 메시지를 출력하고 다시 입력받습니다.
- 정답 입력의 `0`은 정답으로 인정되지 않고 힌트를 보여준 뒤 다시 물어봅니다. 정답으로 받는 값은 항상 1~4입니다.
- `Ctrl+C`(KeyboardInterrupt)나 입력 종료(EOFError)가 발생하면 안내 메시지를 출력하고 데이터를 저장한 뒤 안전하게 종료합니다.
- `state.json`이 없으면 기본 퀴즈 6개로 시작하고, 파일이 손상되었으면 안내 후 기본 퀴즈로 복구합니다.
- 저장된 퀴즈/기록 중 형식이 깨진 항목은 건너뛰고, 쓸 수 있는 데이터만 불러옵니다.

## 5. 파일 구조

```
codyssey-e1-2-quizgame-sg/
├── main.py       # 프로그램 전체 코드 (Storage, Quiz, QuizGame 클래스)
├── state.json    # 퀴즈 목록, 최고 점수, 게임 기록을 저장하는 데이터 파일
├── .gitignore    # Git이 추적하지 않을 파일 목록
├── screenshots   # Git clone, pull, oneline graph 실습 스크린샷 저장
└── README.md     # 프로젝트 설명 문서
```

### 클래스 구조 (`main.py`)

| 클래스 | 역할 | 주요 속성 | 주요 메서드 |
| --- | --- | --- | --- |
| `Storage` | 파일 저장/불러오기 담당 | `path` | `load()`, `save()` |
| `Quiz` | 퀴즈 한 문제를 표현 | `question`, `choices`, `answer`, `hint` | `show()`, `is_correct()`, `answer_text()`, `has_hint()`, `show_hint()`, `to_dict()` |
| `QuizGame` | 게임 전체 관리 | `quizzes`, `best_score`, `best_correct`, `best_total`, `history` | `run()`, `show_menu()`, `play()`, `add_quiz()`, `delete_quiz()`, `show_list()`, `show_score()`, `show_history()`, `ask_number()`, `ask_answer()`, `ask_count()`, `shuffled_quizzes()`, `load()`, `save()` |

## 6. 데이터 파일 설명 (`state.json`)

- **경로**: 프로젝트 루트의 `state.json` (`main.py`와 같은 폴더)
- **인코딩**: UTF-8 (`ensure_ascii=False`로 한글이 그대로 저장됩니다)
- **역할**: 퀴즈 목록, 최고 점수, 게임 기록을 저장해 프로그램을 다시 실행해도 데이터가 유지되도록 합니다.
- **생성 시점**: 파일이 없으면 첫 실행 때 기본 퀴즈로 자동 생성됩니다.

### 필드 구조

| 키 | 타입 | 설명 |
| --- | --- | --- |
| `quizzes` | list | 퀴즈 목록 |
| `quizzes[].question` | str | 문제 |
| `quizzes[].choices` | list(str, 4개) | 선택지 4개 |
| `quizzes[].answer` | int (1~4) | 정답 번호 |
| `quizzes[].hint` | str | 힌트 (없으면 빈 문자열) |
| `best_score` | int | 최고 점수 (100점 만점, 힌트 차감 반영) |
| `best_correct` | int | 최고 점수를 받았을 때 맞힌 문제 수 |
| `best_total` | int | 최고 점수를 받았을 때 푼 문제 수 |
| `history` | list | 게임 기록 목록 |
| `history[].date` | str | 게임을 끝낸 날짜/시간 (`YYYY-MM-DD HH:MM:SS`) |
| `history[].total` | int | 그 판에서 푼 문제 수 |
| `history[].correct` | int | 그 판에서 맞힌 문제 수 |
| `history[].score` | int | 그 판의 점수 |

### 예시

```json
{
  "quizzes": [
    {
      "question": "파이썬에서 정수를 나타내는 자료형은?",
      "choices": ["int", "str", "bool", "list"],
      "answer": 1,
      "hint": "integer(정수)를 줄인 이름입니다."
    }
  ],
  "best_score": 45,
  "best_correct": 1,
  "best_total": 2,
  "history": [
    {
      "date": "2026-08-21 03:13:09",
      "total": 2,
      "correct": 1,
      "score": 45
    }
  ]
}
```
