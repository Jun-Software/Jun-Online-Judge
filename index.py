from flask import *
import subprocess
from threading import Timer
from pysmx.SM3 import digest
import zipfile
from config import *
import pickle
import shutil
import shlex
import os
import sys
from flaskext.markdown import *
# from gevent import monkey
# monkey.patch_all()

flag = False
def kill_command(obj):
    global flag
    flag = True
    obj.kill()

def run(name: str, count: int):
    global flag
    flag = False
    result = 'Accepted'
    for i in range(1, count + 1):
        in_file = 'problem/' + name + '/' + str(i) + '.in'
        out_file = 'problem/' + name + '/' + str(i) + '.out'
        file_name = 'problem/' + name + '/' + name + '.code'
        obj = subprocess.Popen(shlex.split(judge_command.format(file_name)), stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE, universal_newlines = True)
        timer = Timer(2, kill_command, [obj])
        try:
            timer.start()
            with open(in_file) as f:
                lines = f.readlines()
            for line in lines:
                obj.stdin.write(line)
            obj_out, obj_err = obj.communicate()
            if obj_err == '':
                with open(out_file) as f:
                    context = f.read()
                if context == obj_out:
                    pass
                else:
                    if flag == True:
                        result = 'Time Limit Exceeded'
                    else:
                        result = 'Wrong Answer'
            else:
                result = 'Compile Error'
        except:
            result = 'System Error'
        finally:
            timer.cancel()
    return result

try:
    with open('data.dat', 'rb') as f:
        problems = pickle.load(f)
except:
    problems = []
try:
    with open('user.dat', 'rb') as f:
        users = pickle.load(f)
except:
    users = []
try:
    os.mkdir('problem/')
except:
    pass
app = Flask(__name__)
app.config['SECRET_KEY'] = admin_password
Markdown(app)
@app.route('/', methods = ['GET'])
def index():
    if session.get('username') is None:
        return render_template('index.html', problems = problems)
    return render_template('index_logined.html', username = session.get('username'), problems = problems, ac = session.get('ac'))

@app.route('/<path:ojpath>', methods = ['GET', 'POST'])
def problem(ojpath):
    for problem in problems:
        if problem['id'] == str(ojpath):
            if request.method == 'POST':
                file = request.files.get('file')
                file.save('problem/' + problem['id'] + '/' + problem['id'] + '.code')
                with open('problem/' + problem['id'] + '/' + problem['id'] + '.code') as f:
                    code = f.read()
                    if ('__builtins__' in code or 'exec' in code or 'eval' in code or 'import' in code or 'open' in code):
                        result = "Dangerous Syscalls"
                result = run(str(problem['id']), int(problem['count']))
                global user
                if result == 'Accepted' and session.get('username') is not None:
                    global users
                    for user in users:
                        if user['username'] == session.get('username'):
                            user['ac'].append(problem['id'])
                            session['ac'] = user['ac']
                            break
                    with open('user.dat', 'wb') as f:
                        pickle.dump(users, f)
                return render_template("test.html", result = result)
            elif request.method == 'GET':
                return render_template('problem.html', problem_description = problem['description'], problem_id = problem['id'], language = judge_language)
    return "404 Not Found"

@app.route('/login')
def login():
    return render_template('login.html')
    
@app.route('/admin', methods = ['POST'])
def admin():
    passwd = request.values.get('password')
    global admin_password
    if passwd == admin_password:
        return render_template('problem_manager.html', problems = problems)
    return "403 Forbidden"

@app.route('/api/problem', methods = ['POST'])
def problem_api():
    Type = request.values.get('type')
    problem_id = request.values.get('id')
    problem_name = request.values.get('name')
    problem_description = request.values.get('description')
    zip_file = request.files.get('file')
    problem_count = request.values.get('count')
    if Type == 'add':
        os.mkdir('problem/' + problem_id + '/')
        zip_file.save('problem/' + problem_id + '/' + problem_id + '.zip')
        zipfile.ZipFile('problem/' + problem_id + '/' + problem_id + '.zip').extractall('problem/' + problem_id + '/')
        problems.append({'id': problem_id, 'name': problem_name, 'description': problem_description, 'count': problem_count})
        with open('data.dat', 'wb') as f:
            pickle.dump(problems, f)
    elif Type == 'del':
        for problem in problems:
            if problem['id'] == problem_id:
                problems.remove(problem)
                shutil.rmtree('problem/' + problem_id + '/')
        with open('data.dat', 'wb') as f:
            pickle.dump(problems, f)
    else:
        return '404 Not Found'
    global password
    return render_template('redirect.html', passwd = password)

@app.route("/api/login", methods = ['POST'])
def login_api():
    username = request.values.get('username')
    password = request.values.get('password')
    global users
    for user in users:
        if user['username'] == username and user['password'] == digest(password):
            session['username'] = username
            session['ac'] = user['ac']
            break
    return redirect('/')

@app.route("/api/register", methods = ['POST'])
def register_api():
    username = request.values.get('username')
    password = digest(request.values.get('password'))
    email = request.values.get('email')
    flag = True
    for user in users:
        if user['username'] == username:
            flag = False
            break
    if flag == False:
        return render_template('login_redirect.html', message = "Username is already.")
    users.append({'username': username, 'password': password, 'email': email, 'ac': []})
    with open('user.dat', 'wb') as f:
        pickle.dump(users, f)
    session['username'] = username
    session['ac'] = []
    return redirect('/')

if __name__ == '__main__':
    # from gevent import pywsgi
    # server = pywsgi.WSGIServer(('0.0.0.0', 80), app)
    # server.serve_forever()
    app.run('0.0.0.0', port = 80)
