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
from markdown import markdown
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
        obj_out = ''
        lst = judge_command.split('|')
        for j in lst:
            obj = subprocess.Popen(shlex.split(j), stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE, universal_newlines = True)
            timer = Timer(2, kill_command, [obj])
            try:
                timer.start()
                with open(in_file) as f:
                    lines = f.readlines()
                for line in lines:
                    obj.stdin.write(line)
                _obj_out, _obj_err = obj.communicate()
                _obj_out = _obj_out.strip(' ')
                _obj_out = _obj_out.strip('\n')
                _obj_out = _obj_out.strip('\r')
                obj_out += _obj_out
                if _obj_err == '':
                    pass
                else:
                    result = 'Compile Error'
            except:
                result = 'System Error'
            finally:
                timer.cancel()
        with open(out_file) as f:
            context = f.read()
        context = context.strip(' ')
        context = context.strip('\n')
        context = context.strip('\r')
        if context == obj_out:
            pass
        else:
            if flag == True:
                result = 'Time Limit Exceeded'
            else:
                result = 'Wrong Answer'
    return result

def createBackup(outFullName):
    dirpath = os.getcwd() + '/problem'
    zip = zipfile.ZipFile(outFullName, "w", zipfile.ZIP_DEFLATED)
    for path, dirnames, filenames in os.walk(dirpath):
        print(path, dirnames, filenames)
        fpath = path.replace(os.getcwd(), '')
        for filename in filenames:
            zip.write(os.path.join(path, filename), os.path.join(fpath, filename))
    zip.write(os.path.join(os.getcwd(), 'data.dat'), os.path.join('', 'data.dat'))
    zip.write(os.path.join(os.getcwd(), 'user.dat'), os.path.join('', 'user.dat'))
    zip.close()
problems = []
try:
    with open('data.dat', 'rb') as f:
        problems = pickle.load(f)
except:
    problems = []
    with open('data.dat', 'wb') as f:
        pickle.dump(problems, f)
users = []
try:
    with open('user.dat', 'rb') as f:
        users = pickle.load(f)
except:
    users = [{'username': 'admin', 'password': 'admin_password', 'ac': [], 'profile': '', 'ban': False}]
    with open('user.dat', 'wb') as f:
        pickle.dump(users, f)
try:
    os.mkdir('problem/')
except:
    pass
try:
    os.mkdir('temp/')
except:
    pass

def user_sort_key(elem):
    return len(elem['ac'])

app = Flask(__name__)
app.config['SECRET_KEY'] = admin_password
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
                file.save('temp/' + problem['id'] + '/' + problem['id'] + '.' + judge_language_ext)
                with open('temp/' + problem['id'] + '/' + problem['id'] + '.' + judge_language_ext) as f:
                    code = f.read()
                    if ('__builtins__' in code or 'exec' in code or 'eval' in code or 'import' in code or 'open' in code or 'system' in code):
                        result = "Dangerous Syscalls"
                result = run(str(problem['id']), int(problem['count']))
                global user
                if result == 'Accepted' and session.get('username') is not None and problem['id'] not in session.get('ac'):
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
                try:
                    os.mkdir('temp/' + problem['id'] + '/')
                except:
                    pass
                return render_template('problem.html', problem_description = markdown(problem['description']), problem_id = problem['id'], language = judge_language)
    return "404 Not Found"

@app.route('/contest')
def contest():
    problems = request.values.get('problems')
    if session.get('ac') == None:
        return redirect('/login')
    minute = request.values.get('time')
    return render_template('contest.html', time = minute, len = len, problems = problems)

@app.route('/frame_contest')
def frame_contest():
    problems = request.values.get('problems').split(';')
    return render_template('contest_problems.html', problems = problems, ac = session.get('ac'))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login_admin')
def login_admin():
    return render_template('login_admin.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')
    
@app.route('/admin', methods = ['POST'])
def admin():
    passwd = request.values.get('password')
    global admin_password
    global problem_template
    if passwd == admin_password:
        return render_template('admin.html', problems = problems, admin_password = admin_password, users = users, len = len, problem_template = problem_template)
    return "403 Forbidden"

@app.route('/backup')
def backup():
    passwd = request.values.get("password")
    global admin_password
    if passwd == admin_password:
        createBackup("static/backup.zip")
        return redirect("/static/backup.zip")
    return "403 Forbidden"

@app.route('/rank')
def rank():
    users.sort(key = user_sort_key)
    return render_template('rank.html', users = users, len = len)

@app.route('/change_profile', methods = ["GET", "POST"])
def change_profile():
    global users
    if request.method == "GET":
        if session.get('username') is not None:
            for user in users:
                if user['username'] == session.get('username'):
                    return render_template('change_profile.html', user = user)
        return redirect('/login')
    username = session.get('username')
    profile = request.values.get('profile')
    cnt = 0
    while profile.find('```') != -1:
        cnt += 1
        if cnt % 2 != 0:
            profile = profile.replace('```', '<textarea>', 1)
        else:
            profile = profile.replace('```', '</textarea>', 1)
    cnt = 0
    while profile.find('`') != -1:
        cnt += 1
        if cnt % 2 != 0:
            profile = profile.replace('`', '<textarea>', 1)
        else:
            profile = profile.replace('`', '</textarea>', 1)
    for user in users:
        if username == user['username']:
            user['profile'] = markdown(profile)
            break
    with open('user.dat', 'wb') as f:
        pickle.dump(users, f)
    return redirect('/')

@app.route('/profile')
def profile():
    username = request.values.get('username')
    if username is None:
        return redirect('/')
    global users
    for user in users:
        if user['username'] == username:
            return render_template('profile.html', user = user)
    return redirect('/')


@app.route('/api/problem', methods = ['POST'])
def problem_api():
    Type = request.values.get('type')
    problem_id = request.values.get('id')
    problem_name = request.values.get('name')
    problem_description = request.values.get('description')
    zip_file = request.files.get('file')
    problem_count = request.values.get('count')
    if Type == 'add':
        cnt = 0
        while problem_description.find('```') != -1:
            cnt += 1
            if cnt % 2 != 0:
                problem_description = problem_description.replace('```', '<textarea>', 1)
            else:
                problem_description = problem_description.replace('```', '</textarea>', 1)
        cnt = 0
        while problem_description.find('`') != -1:
            cnt += 1
            if cnt % 2 != 0:
                problem_description = problem_description.replace('`', '<textarea>', 1)
            else:
                problem_description = problem_description.replace('`', '</textarea>', 1)
        os.mkdir('problem/' + problem_id + '/')
        os.mkdir('temp/' + problem_id + '/')
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
    return render_template('redirect.html', passwd = admin_password)

@app.route('/api/user', methods = ['POST'])
def user_api():
    Type = request.values.get('type')
    username = request.values.get('username')
    password = request.values.get('password')
    global users
    if Type == 'add':
        flag = True
        for user in users:
            if user['username'] == username:
                flag = False
                break
        if flag == False:
            return "Username is already."
        users.append({'username': username, 'password': password, 'email': '', 'ac': [], 'profile': '', 'ban': False})
        with open('user.dat', 'wb') as f:
            pickle.dump(users, f)
    elif Type == 'del':
        if username == 'admin':
            return "You cannot delete the Administrator account."
        for user in users:
            if user['username'] == username:
                users.remove(user)
                break
    elif Type == 'ban':
        if username == 'admin':
            return "You cannot ban the Administrator account."
        for user in users:
            if user['username'] == username:
                user['ban'] = True
                break
    else:
        return '404 Not Found'
    with open('user.dat', 'wb') as f:
        pickle.dump(users, f)
    global admin_password
    return render_template('redirect.html', passwd = admin_password)

@app.route("/api/login", methods = ['POST'])
def login_api():
    username = request.values.get('username')
    password = request.values.get('password')
    global users
    for user in users:
        if user['username'] == username and user['password'] == 'admin_password':
            session['username'] = username
            session['ac'] = user['ac']
            break
        if user['username'] == username and user['password'] == digest(password):
            if user['ban'] == True:
                return render_template('login_redirect.html', message = "Your account is ban.")
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
    users.append({'username': username, 'password': password, 'email': email, 'ac': [], 'profile': ''})
    with open('user.dat', 'wb') as f:
        pickle.dump(users, f)
    session['username'] = username
    session['ac'] = []
    return redirect('/')

@app.route("/api/backup", methods = ["POST"])
def upload_backup():
    backup_file = request.files.get('file')
    passwd = request.values.get('passwd')
    backup_file.save('backup.zip')
    zipfile.ZipFile('backup.zip').extractall()
    global problems
    try:
        with open('data.dat', 'rb') as f:
            problems = pickle.load(f)
    except:
        problems = []
    global users
    try:
        with open('user.dat', 'rb') as f:
            users = pickle.load(f)
    except:
        users = []
    try:
        os.mkdir('problem/')
    except:
        pass
    return render_template("redirect.html", passwd = passwd)


if __name__ == '__main__':
    # from gevent import pywsgi
    # server = pywsgi.WSGIServer(('0.0.0.0', 80), app)
    # server.serve_forever()
    app.run('0.0.0.0', port = 80)
