import hashlib
import re

from flask import Flask, render_template, request, redirect, url_for, session, abort, jsonify

from myDb import get_db_connection, createUser

app = Flask(__name__)

app.secret_key = 'myBoY'
PATH_EDU_MATERIAL = [
    "static/theories/theory",
    "static/practicate/practicate",
    "static/tests/test"
]


# region Здесь функции для упрощения
def get_path_edu_material(index, indexOfMat):
    return PATH_EDU_MATERIAL[index] + f"{indexOfMat}.txt"


def read_edu_material(index, indexOfMat):
    if indexOfMat == '': return ""
    path = get_path_edu_material(index, indexOfMat)
    return read_file(path)


def write_edu_material(index, indexOfMat, text):
    if indexOfMat == '': return ""
    path = get_path_edu_material(index, indexOfMat)
    write_file(path, text)
    return


def read_file(path):
    with open(path, 'r', encoding="utf-8") as f:
        text = f.read()
        return text


def write_file(path, string):
    with open(path, 'w', encoding="utf-8") as f:
        f.write(string.replace('\r\n', '\n'))


def get_text_as_components(text):
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


def get_questions_as_components(text):
    questions = []
    lines = text.strip().split('\n')
    i = 0

    while i < len(lines):
        # Извлекаем номер вопроса и текст вопроса
        match = re.match(r"(\d+)(.*)", lines[i])
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


# endregion


# region Events for processing user actions
@app.route('/', methods=["GET", "POST"])
def index():
    return render_template('main.html')


@app.route('/theory', methods=["GET", "POST"])
def theory():
    theory1 = get_text_as_components(read_file(get_path_edu_material(0, 1)))
    theory2 = get_text_as_components(read_file(get_path_edu_material(0, 2)))
    theory3 = get_text_as_components(read_file(get_path_edu_material(0, 3)))
    theory4 = get_text_as_components(read_file(get_path_edu_material(0, 4)))
    theory5 = get_text_as_components(read_file(get_path_edu_material(0, 5)))

    return render_template('theory.html', theory1=theory1, theory2=theory2, theory3=theory3, theory4=theory4,
                           theory5=theory5)


@app.route('/practicate', methods=["GET", "POST"])
def practicate():
    lab1 = get_text_as_components(read_file(get_path_edu_material(1, 1)))
    lab2 = get_text_as_components(read_file(get_path_edu_material(1, 2)))
    lab3 = get_text_as_components(read_file(get_path_edu_material(1, 3)))

    return render_template('practicate.html', pract1=lab1, pract2=lab2, pract3=lab3)


@app.route('/tests', methods=["GET", "POST"])
def tests():
    tab = request.args.get('test', '')
    check = get_test_availability().get_json()
    if check.get('test'+tab) == 0 and not session.get('admin'):
        return redirect('/tests')

    test1 = get_questions_as_components(read_file(get_path_edu_material(2, 1)))
    test2 = get_questions_as_components(read_file(get_path_edu_material(2, 2)))
    test3 = get_questions_as_components(read_file(get_path_edu_material(2, 3)))
    if request.method == 'POST':
        user_answers = request.form
        score = 0
        count_questions = 0
        current_test = -1
        if tab == "1":
            current_test = test1
        elif tab == "2":
            current_test = test2
        elif tab == "3":
            current_test = test3
        if current_test != -1:
            for component in current_test:
                question_number = component['i']
                correct_answer = component['correct_answer']
                user_answer = user_answers.get(f'answer_{question_number}')
                count_questions += 1
                if user_answer == correct_answer:
                    score += 1
            score = (score / count_questions) * 100

            return render_template('tests.html', test=tab, score=score, test1=test1, test2=test2, test3=test3)

    return render_template('tests.html', test=tab, test1=test1, test2=test2, test3=test3)


@app.route('/getTest', methods=["GET", "POST"])
def check_availability_test():
    index_test = request.args.get("index", "")
    if session.get('admin'):
        return jsonify({'status': 'success', 'redirect': f'tests?test={index_test}'})
    c = get_db_connection()
    test_availability = c.execute('SELECT availability FROM tests WHERE id = ?', (index_test,)).fetchone()
    c.close()
    if bool(test_availability['availability']):
        return jsonify({'status': 'success', 'redirect': f'tests?test={index_test}'})
    return jsonify({'status': 'error', 'message': 'Похоже учитель еще не открыл доступ к этому тесту.'})


@app.route('/getTestAvailability', methods=["GET", "POST"])
def get_test_availability():
    c = get_db_connection()
    tests = c.execute("SELECT * FROM tests").fetchall()
    return jsonify(
        {'test1': tests[0]['availability'], 'test2': tests[1]['availability'], 'test3': tests[2]['availability']})


@app.route('/changeAvailabilityTest', methods=["GET", "POST"])
def change_test_availability():
    i = request.get_json()
    c = get_db_connection()
    now_availability = c.execute("SELECT availability FROM tests WHERE id = ?", (i,)).fetchone()
    if now_availability["availability"] == 1:
        now_availability = 0
    else:
        now_availability = 1
    c.execute("UPDATE tests SET availability = ? WHERE id = ?", (now_availability, i,))
    c.commit()
    c.close()
    return jsonify('success')

@app.route('/admin', methods=["GET", "POST"])
def admin_panel():
    if not session.get('admin'):
        abort(404)
    if request.method == 'POST':
        action = request.form.get('form_id')
        if action == 'save_user':
            login = request.form.get('login')
            password = request.form['password']
            newpassword = hashlib.sha256(password.encode('utf-8')).hexdigest()
            admin = request.form.get('admin', '0')

            conn = get_db_connection()
            if password == "":
                conn.execute('UPDATE users SET admin = ? WHERE username = ?', (admin, login,)).fetchone()
            else:
                conn.execute('UPDATE users SET password = ?, admin = ? WHERE username = ?',
                             (newpassword, admin, login,)).fetchone()
            conn.commit()
            conn.close()
        elif action == 'delete_user':
            login = request.form.get('login')
            conn = get_db_connection()
            conn.execute('DELETE FROM users WHERE username = ?', (login,)).fetchone()
            conn.commit()
            conn.close()
        elif action == 'create_user':
            login = request.form.get('newLogin')
            password = request.form.get('newPassword')
            admin = request.form.get('newAdmin', '0')
            if login == "" or password == "":
                return render_template('admin_panel.html', values_error='create_user', active_tab='accounts',
                                       accounts=get_users())
            createUser(login, password, admin)

        elif action == 'save_lectures':
            index = request.args.get('theory', '')
            text = request.form.get('lectures')
            write_edu_material(0, index, text)

        elif action == 'save_labs':
            index = request.args.get('lab', '')
            text = request.form.get('labs')
            write_edu_material(1, index, text)

        elif action == 'save_tests':
            index = request.args.get('test', '')
            text = request.form.get('test')
            write_edu_material(2, index, text)

    tab = request.args.get('tab', 'intro')
    theory = request.args.get('theory', '')
    theory = read_edu_material(0, theory)
    lab = request.args.get('lab', '')
    lab = read_edu_material(1, lab)
    test = request.args.get('test', '')
    test = read_edu_material(2, test)

    return render_template('admin_panel.html', active_tab=tab, theory=theory, lab=lab, test=test, accounts=get_users())


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


@app.route('/change-theme', methods=['POST'])
def set_theme():
    data = request.get_json()
    theme = data.get('theme')
    session['theme'] = theme
    return jsonify({'message': 'Тема успешно сохранена!', 'theme': theme}), 200


@app.route('/change-theme', methods=['GET'])
def get_theme():
    theme = session.get('theme', 'light')
    return jsonify({'theme': theme}), 200


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


# endregion


if __name__ == "__main__":
    app.run()
