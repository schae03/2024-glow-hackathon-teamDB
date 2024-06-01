from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# FAQ 목록 고정
FAQ = [
    (1, "Q. 우산과 같이 여러 재질이 섞여 있는 경우는 어떻게 배출해야 할까요?", 
     """A. 재질별로 분리배출 하는 것이 원칙입니다.<br><br>
     우산의 경우, 뼈대는 철, 고철로 분리배출하면 재활용이 가능하고 손잡이는 보통 플라스틱, 나무, 혼합물질 등으로 되어 있는데, 플라스틱을 제외하면 모두 일반 쓰레기에 해당합니다. 비를 막아주는 천이나 비닐 또한 일반 쓰레기에 해당한다고 할 수 있습니다. <br>
     허나, 분리가 어려운 경우에는 우산 전체를 고철류로 배출해야 합니다. <br>
     """),
    (2, "Q. 음식물 쓰레기인지 일반 쓰레기인지는 어떻게 구분해야 하나요?", 
     """A. 음식물 쓰레기인지 아닌지를 구분하는 기준은 '동물이 먹을 수 있느냐' 입니다. <br><br>
     음식물 쓰레기는 수거된 후 퇴비나 동물 사료로 재활용되기 때문에 동물이 먹을 수 없는 것에 대해서는 일반 쓰레기로 분류하여야 합니다. <br><br>

     사과, 귤, 바나나 등 부드러운 껍질은 음식물 쓰레기입니다. (수박껍질과 같이 부피가 큰 건 잘라서 넣어야 합니다) <br>
     하지만 호두, 밤, 땅콩, 코코넛, 파인애플 등 딱딱한 껍질은 일반 쓰레기로 버려야 합니다.<br> 
     닭, 소, 돼지의 뼈, 계란 껍데기, 차 찌꺼기, 생선 뼈, 패류 껍데기, 과일 씨, 양파나 옥수수 껍질, 쪽파나 대파, 미나리 등의 뿌리는 모두 음식물 쓰레기로 헷갈릴 수 있으나 일반 쓰레기로 분류됩니다.<br>
     """),
    (3, "Q. 분리 배출 시 헷갈리지 않게 주의해야 하는 쓰레기에는 어떤 것이 있나요?", 
     """A. 재활용품인 듯하지만 종량제 봉투에 넣어야 하는 쓰레기 3가지에 대해 알려드리겠습니다.<br><br>

     1. 씻어도 이물질이 제거되지 않은 용기류<br>
     : 예를 들어, 치킨을 포장했을 때 딸려오는 치킨을 담은 상자는 기름 등 이물질이 많이 묻어있고 다른 재질과 혼합되어 재활용이 어렵기 때문에 종량제 봉투에 버려야 합니다. <br>또 세척하지 않은 '컵밥'류와 '컵라면 용기' 역시 재활용이 어렵고, 마요네즈나 케찹 등이 담겼던 용기는 깨끗하게 세척 후 말릴 경우 재활용이 가능하나 내용물이 담긴 채 버린다면 재활용이 불가능하기 때문에 종량제 봉투에 넣어야 합니다.<br><br>

     2. 오해하기 쉬운 품목<br>
     : 환경부에서는 재활용품으로 보이나 재활용이 안되는 대표적인 품목으로 과일망을 비롯한 '과일 포장재', '깨진 병', '도자기류', '보온,보냉팩', 볼펜, 샤프, 칫솔을 비롯한 '문구류', '고무장갑', '슬리퍼', '기저귀', '화장지' 등을 꼽았습니다.<br><br>

     3. 폐비닐<br>
     : 폐비닐은 내용물을 비우고 헹군 뒤 깨끗하게 말렸을 경우는 분리배출이 가능하나 나머지 경우는 모두 종량제 봉투에 버려야 합니다. 또한 식탁보, 이불커버 역시 재활용 대상이 아닌 종량제 봉투로 배출해야 합니다.<br>
     """)
]

def init_db():
    with sqlite3.connect("database.db") as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS questions
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      title TEXT NOT NULL,
                      content TEXT NOT NULL)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS comments
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      question_id INTEGER NOT NULL,
                      content TEXT NOT NULL)''')

init_db()

@app.route('/')
def index():
    with sqlite3.connect("database.db") as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, title FROM questions ORDER BY id DESC")
        questions = cur.fetchall()
    return render_template('index.html', faqs=FAQ, questions=questions)

@app.route('/question/<int:question_id>', methods=['GET', 'POST'])
def question(question_id):
    if request.method == 'POST':
        content = request.form['content']
        with sqlite3.connect("database.db") as conn:
            conn.execute("INSERT INTO comments (question_id, content) VALUES (?, ?)", (question_id, content))
        return redirect(url_for('question', question_id=question_id))
    
    with sqlite3.connect("database.db") as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM questions WHERE id=?", (question_id,))
        question = cur.fetchone()
        cur.execute("SELECT * FROM comments WHERE question_id=? ORDER BY id", (question_id,))
        comments = cur.fetchall()

    return render_template('question.html', question=question, comments=comments)

@app.route('/faq/<int:faq_id>', methods=['GET'])
def faq(faq_id):
    faq = next((item for item in FAQ if item[0] == faq_id), None)
    return render_template('faq.html', faq=faq)

@app.route('/add', methods=['GET', 'POST'])
def add_question():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        with sqlite3.connect("database.db") as conn:
            conn.execute("INSERT INTO questions (title, content) VALUES (?, ?)", (title, content))
        return redirect(url_for('index'))
    return render_template('add_question.html')

#if __name__ == '__main__':
#    app.run(debug=True)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')

