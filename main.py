from flask import Flask, render_template, request, send_file, redirect, url_for, session
from myDb import get_db_connection, createUser, createTables
import hashlib
import re
import datetime
import logging

app = Flask(__name__)

app.secret_key = 'myBoY'


# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')


def read_file(path):
    with open(path, 'r', encoding="utf-8") as f:
        text = f.read()
        return text


def write_file(path, string):
    with open(path, 'w', encoding="utf-8") as f:
        f.write(string.replace('\r\n', '\n'))


def getTextAsComponents(text):
    components = []
    while len(text) > 0:
        # Найти индекс первой новой строки
        int_index = text.find('\n')

        # Если новой строки нет, берем остаток текста
        if int_index == -1:
            line = text
            text = ''
        else:
            line = text[:int_index]
            text = text[int_index + 1:]  # Убираем обработанную строку

        # Определяем тип компонента
        if line.startswith('###'):
            components.append({'type': 'h2', 'content': line[3:].strip()})
        elif line.startswith('##'):
            components.append({'type': 'h1', 'content': line[2:].strip()})
        else:
            components.append({'type': 'p', 'content': line.strip()})

    return components


def getQuestions(text):
    questions = []
    lines = text.strip().split('\n')
    i = 0

    while i < len(lines):
        # Извлекаем номер вопроса и текст вопроса
        match = re.match(r"(\d+)(.*?\?)", lines[i])
        if match:
            i_num = int(match.group(1))
            question = match.group(2).strip()
        else:
            i += 1
            continue
        i += 1

        # Извлекаем варианты ответов и правильный ответ
        if i < len(lines):
            options = lines[i].split('|')
            correct_answer = None
            cleaned_options = []
            for option in options:
                if option.startswith('*'):
                    correct_answer = option[1:]
                    cleaned_options.append(option[1:])
                else:
                    cleaned_options.append(option)

            if correct_answer is None:
                correct_answer = cleaned_options[0]
            questions.append({
                'i': i_num,
                'question': question,
                'options': cleaned_options,
                'correct_answer': correct_answer
            })
            i += 1
        else:
            break

    return questions


@app.route('/', methods=["GET", "POST"])
def index():
    # count = read_file()
    # return render_template('main.html', count=count) передача переменных

    return render_template('main.html')


@app.route('/theory', methods=["GET", "POST"])
def theory():
    theory1 = getTextAsComponents(read_file("static/theories/theory1.txt"))
    theory2 = getTextAsComponents(read_file("static/theories/theory2.txt"))
    theory3 = getTextAsComponents(read_file("static/theories/theory3.txt"))
    theory4 = getTextAsComponents(read_file("static/theories/theory4.txt"))
    theory5 = getTextAsComponents(read_file("static/theories/theory5.txt"))

    return render_template('theory.html', theory1=theory1, theory2=theory2, theory3=theory3, theory4=theory4,
                           theory5=theory5)


@app.route('/practicate', methods=["GET", "POST"])
def practicate():
    lab1 = getTextAsComponents(read_file("static/practicate/practicate1.txt"))
    lab2 = getTextAsComponents(read_file("static/practicate/practicate2.txt"))
    lab3 = getTextAsComponents(read_file("static/practicate/practicate3.txt"))

    return render_template('practicate.html', pract1=lab1, pract2=lab2, pract3=lab3)


@app.route('/tests', methods=["GET", "POST"])
def tests():
    tab = request.args.get('test', '')
    test1 = getQuestions(read_file("static/tests/test1.txt"))
    if request.method == 'POST':
        user_answers = request.form  # Получаем данные формы в словаре
        score = 0
        count_questions = 0
        for component in test1:
            question_number = component['i']
            correct_answer = component['correct_answer']
            user_answer = user_answers.get(f'answer_{question_number}')
            count_questions += 1
            if user_answer == correct_answer:
                score += 1
        score = (score / count_questions) * 100
        return render_template('tests.html', test=tab, score=score, test1=test1)

    return render_template('tests.html', test=tab, test1=test1)


def get_users():
    conn = get_db_connection()
    usersDb = conn.execute('SELECT * FROM users').fetchall()  # Получаем все записи
    conn.close()

    # Обработка данных
    users = []
    for user in usersDb:
        user_data = {
            'id': user[0],
            'login': user[1],
            # 'password': user[2],
            'admin': user[3]
        }
        users.append(user_data)

    return users


def readTheory(index):
    if index == '': return ""
    path = f"static/theories/theory{index}.txt"
    return read_file(path)


def writeTheory(index, text):
    if index == '': return ""
    path = f"static/theories/theory{index}.txt"
    write_file(path, text)
    return


@app.route('/admin', methods=["GET", "POST"])
def admin_panel():
    if request.method == 'POST':
        action = request.form.get('form_id')
        if action == 'save_user':
            login = request.form.get('login')
            password = request.form['password']
            newpassword = hashlib.sha256(password.encode('utf-8')).hexdigest()
            admin = request.form.get('admin', 'false')

            conn = get_db_connection()
            if password == "":
                updateUser = conn.execute('UPDATE users SET admin = ? WHERE username = ?', (admin, login,)).fetchone()
            else:
                updateUser = conn.execute('UPDATE users SET password = ?, admin = ? WHERE username = ?',
                                          (newpassword, admin, login,)).fetchone()
            conn.commit()
            conn.close()
        elif action == 'save_lectures':
            index = request.args.get('theory', '')
            theory = request.form.get('lectures')
            writeTheory(index, theory)

    tab = request.args.get('tab', 'intro')
    theory = request.args.get('theory', '')
    theory = readTheory(theory)

    return render_template('admin_panel.html', active_tab=tab, theory=theory, accounts=get_users())


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        login = request.form.get('login')
        passw = request.form.get('password')
        hashed_password = hashlib.sha256(passw.encode('utf-8')).hexdigest()

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (login,)).fetchone()
        conn.close()

        if user and user['password'] == hashed_password:
            if user['admin'] == 1:
                session['admin'] = True
            session['username'] = login
            return redirect(url_for('index'))
        else:
            return render_template('login.html', passw=False)
    return render_template('login.html')


@app.route('/logout', methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/download')
def download_file():
    # path = "D:\programms\openserver\domains\localhost\static\images\privet.png"
    # count = read_file()
    # count = int(count) + 1
    # write_file(str(count))
    return send_file(path, as_attachment=True)


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


if __name__ == "__main__":
    app.run(host='192.168.1.34', port='80')
