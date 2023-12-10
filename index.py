from flask import *
import subprocess
from threading import Timer
import zipfile
import pickle
import shutil
import os
import sys
from flaskext.markdown import *
# from gevent import monkey
# monkey.patch_all()

def kill_command(obj):
    obj.kill()

def run(name: str, count: int):
    result = 'Accepted'
    for i in range(1, count + 1):
        in_file = 'problem/' + name + '/' + str(i) + '.in'
        out_file = 'problem/' + name + '/' + str(i) + '.out'
        file_name = 'problem/' + name + '/' + name + '.py'
        obj = subprocess.Popen(["python3", file_name], stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE, universal_newlines = True)
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
                elif result == 'Accepted':
                    result = 'Wrong Answer / Time Limit Exceeded'
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
    os.mkdir('problem/')
except:
    pass
from config import *
app = Flask(__name__)
Markdown(app)
@app.route('/', methods = ['GET'])
def index():
    return render_template('index.html', problems = problems)
@app.route('/<path:ojpath>', methods = ['GET', 'POST'])
def problem(ojpath):
    for problem in problems:
        if problem['id'] == str(ojpath):
            if request.method == 'POST':
                file = request.files.get('file')
                file.save('problem/' + problem['id'] + '/' + problem['id'] + '.py')
                with open('problem/' + problem['id'] + '/' + problem['id'] + '.py') as f:
                    code = f.read()
                    if ('__builtins__' in code or 'exec' in code or 'eval' in code or 'import' in code or 'open' in code):
                        return render_template('test.html', result = 'Dangerous Syscalls')
                return render_template("test.html", result = run(str(problem['id']), int(problem['count'])))
            elif request.method == 'GET':
                return render_template('problem.html', problem_description = problem['description'], problem_id = problem['id'])
    return "404 Not Found"

@app.route('/login')
def problem_manager():
    return render_template('login.html')
    
@app.route('/admin', methods = ['POST'])
def admin():
    passwd = request.values.get('password')
    global password
    if passwd == password:
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

if __name__ == '__main__':
    # from gevent import pywsgi
    # server = pywsgi.WSGIServer(('0.0.0.0', 80), app)
    # server.serve_forever()
    app.run('0.0.0.0', port = 80)
