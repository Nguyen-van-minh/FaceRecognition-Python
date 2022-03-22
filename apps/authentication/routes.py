from flask import render_template, redirect, request, url_for, Flask, flash, render_template_string, get_flashed_messages, Response
from flask_login import (
    current_user,
    login_user,
    logout_user
)
import csv
import json
import pandas as pd
from apps import login_manager
from apps.authentication import blueprint, db
from apps.authentication.forms import LoginForm, CreateAccountForm, UserDataForm
from apps.authentication.models import Users, IncomeExpenses
from apps.authentication.util import verify_pass
import os
from werkzeug.utils import secure_filename
#---------
import cv2 
import numpy as np 
import face_recognition 
from datetime import datetime
import mysql.connector

app = Flask(__name__)

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="python"
)
mycursor = mydb.cursor()
def themMon(ten):
    sql = "INSERT INTO class (name) VALUES ('"+ten+"')"
    mycursor.execute(sql)
    mydb.commit()

path = 'C:/BTPY/BaiTapCaNhan/apps/authentication/ImagesAttendance'
images = []  
classNames = [] 
myList = os.listdir(path) 

for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}') 
    images.append(curImg) 
    classNames.append(os.path.splitext(cl)[0])
def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) 
        encode = face_recognition.face_encodings(img)[0] 
        encodeList.append(encode)
    return encodeList

encodeListKnown = findEncodings(images)

def danhsachhocsinh(classCode):
    n = []
    mycursor.execute('SELECT * FROM cs where classCode = '+classCode+'')
    studen = mycursor.fetchall()
    for hocsinh in studen:
        n.append(hocsinh)
    return n


camera = cv2.VideoCapture(0)

def gen_frames(id): 
    l = danhsachhocsinh(id)
    now = datetime.now()
    time = now.strftime('%Y-%m-%d %H:%M:%S')
    print(time) 
    check = False
    ok = False
    done = False
    Id = ''
    studenCode = ''
    classCode = id 
    firtName = ''
    lastName = ''

    while True:
        success, img = camera.read()
        imgS = cv2.resize(img,(0,0),None,0.25,0.25) 
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
        facesCurFrame = face_recognition.face_locations(imgS) 
        encodesCurFrame = face_recognition.face_encodings(imgS,facesCurFrame)

        if not success:
            break
        else:
            for encodeFace,faceLoc in zip(encodesCurFrame,facesCurFrame): 
                matches = face_recognition.compare_faces(encodeListKnown,encodeFace) 
                faceDis = face_recognition.face_distance(encodeListKnown,encodeFace)
                matchIndex = np.argmin(faceDis)      
                if matches[matchIndex]: 
                    name = classNames[matchIndex].upper()
                    for i in l:
                        if name == i[1] and i[5]==1:
                            check = True
                            Id = i[0]
                            studenCode = i[1]
                            firtName = i[3]
                            lastName = i[4]
                            break
                        if name == i[1] and i[5] == 2:
                            done = True
                            break
                    if check == True:                                           
                        y1,x2,y2,x1 = faceLoc
                        y1, x2, y2, x1 = y1*4,x2*4,y2*4,x1*4 
                        cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0),2)
                        cv2.rectangle(img,(x1,y2-35),(x2,y2),(0,255,0),cv2.FILLED)
                        cv2.putText(img,name,(x1+6,y2-6),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),2)

                        mycursor.execute('UPDATE cs SET status = 2  WHERE id = '+str(Id)+'')
                        mydb.commit()

                        sql = "INSERT INTO history (studenCode,classCode,firtName,lastName,time) VALUES ('"+studenCode+"','"+classCode+"','"+firtName+"','"+lastName+"','"+time+"')"
                        mycursor.execute(sql)
                        mydb.commit() 

                        check = False
                        ok = True
                    elif done == True:
                        y1,x2,y2,x1 = faceLoc
                        y1, x2, y2, x1 = y1*4,x2*4,y2*4,x1*4 
                        cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,255),2)
                        cv2.rectangle(img,(x1,y2-35),(x2,y2),(0,255,255),cv2.FILLED)
                        cv2.putText(img,name,(x1+6,y2-6),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),2)    
                    else:
                        y1,x2,y2,x1 = faceLoc
                        y1, x2, y2, x1 = y1*4,x2*4,y2*4,x1*4 
                        cv2.rectangle(img,(x1,y1),(x2,y2),(0,0,255),2)
                        cv2.rectangle(img,(x1,y2-35),(x2,y2),(0,0,255),cv2.FILLED)
                        cv2.putText(img,name,(x1+6,y2-6),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),2)

            ret, buffer = cv2.imencode('.jpg', img)
            img = buffer.tobytes()
            yield (b'--img\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + img + b'\r\n')
        if ok == True:              
            break
         
                
@blueprint.route('/video_feed/<classCode>')
def video_feed(classCode):
    id = classCode
    return Response(gen_frames(id), mimetype='multipart/x-mixed-replace; boundary=img')

@blueprint.route('/diemdanh/<id>')
def diemdanh(id):
    
    return render_template('home/diemdanh.html',  id = id)  

@blueprint.route('/lop', methods = ['GET','POST'])
def lop():
    studenCode = request.form.get('studenCode')
    firtName = request.form.get('firtName')
    lastName = request.form.get('lastName')
    classCode = request.form.get('classCode')
    name = request.form.get('monhoc')
    reset = request.form.get('reset')
    check = False

    mycursor.execute("SELECT * FROM cs")
    studen = mycursor.fetchall()

    if reset:
        mycursor.execute("UPDATE cs SET status = 1 where status = 2")
        mydb.commit()  
        return redirect(url_for('authentication_blueprint.lop'))
    if  studenCode:        
        sql = "INSERT INTO cs (studenCode,classCode,firtName,lastName,status) VALUES ('"+studenCode+"','"+classCode+"','"+firtName+"','"+lastName+"','1')"
        mycursor.execute(sql)
        mydb.commit()
        return redirect(url_for('authentication_blueprint.lop'))
    if name:
        mycursor.execute('SELECT * FROM cs where classCode = '+name+'')
        studen = mycursor.fetchall()
        check = True

    mycursor.execute("SELECT * FROM class")
    myresult = mycursor.fetchall()

   
    return render_template('home/lop.html', caclop = myresult, cachocsinh = studen, idMonhoc = name, check = check)

@blueprint.route('/history', methods = ['GET','POST'])
def history(): 
    name = request.form.get('monhoc')
    
    mycursor.execute("SELECT * FROM history")
    studen = mycursor.fetchall()

    if name:
        mycursor.execute('SELECT * FROM history where classCode = '+name+'')
        studen = mycursor.fetchall()

    mycursor.execute("SELECT * FROM class")
    myresult = mycursor.fetchall()

    return render_template('home/history.html', caclop = myresult, cachocsinh = studen)

@blueprint.route('/monhoc', methods = ['GET','POST'])
def monhoc():
    if request.method == 'POST':
        name = request.form["tenmon"]
        sql = "INSERT INTO class (name) VALUES ('"+name+"')"
        mycursor.execute(sql)
        mydb.commit()
    mycursor.execute("SELECT * FROM class")
    myresult = mycursor.fetchall()
    return render_template('home/monhoc.html', cacmon = myresult)  

@blueprint.route('/icon')
def icon():
    return render_template('home/ui-icons.html')

@blueprint.route('/')
def route_default():
    return redirect(url_for('authentication_blueprint.login'))

# Login & Registration


@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)
    if 'login' in request.form:

        # read form data
        username = request.form['username']
        password = request.form['password']

        # Locate user
        user = Users.query.filter_by(username=username).first()

        # Check the password
        if user and verify_pass(password, user.password):

            login_user(user)
            return redirect(url_for('authentication_blueprint.route_default'))

        # Something (user or pass) is not ok
        return render_template('accounts/login.html',
                               msg='Wrong user or password',
                               form=login_form)

    if not current_user.is_authenticated:
        return render_template('accounts/login.html',
                               form=login_form)
    return redirect(url_for('home_blueprint.index'))


@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    create_account_form = CreateAccountForm(request.form)
    if 'register' in request.form:

        username = request.form['username']
        email = request.form['email']

        # Check usename exists
        user = Users.query.filter_by(username=username).first()
        if user:
            return render_template('accounts/register.html',
                                   msg='Username already registered',
                                   success=False,
                                   form=create_account_form)

        # Check email exists
        user = Users.query.filter_by(email=email).first()
        if user:
            return render_template('accounts/register.html',
                                   msg='Email already registered',
                                   success=False,
                                   form=create_account_form)

        # else we can create the user
        user = Users(**request.form)
        db.session.add(user)
        db.session.commit()

        return render_template('accounts/register.html',
                               msg='User created please <a href="/login">login</a>',
                               success=True,
                               form=create_account_form)

    else:
        return render_template('accounts/register.html', form=create_account_form)


@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('authentication_blueprint.login'))


# Errors
@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('home/page-404.html'), 404


@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('home/page-500.html'), 500


# Read file csv to datatable
@blueprint.route('/read_csv', methods=['POST', 'GET'])
def render_file_csv():
    if request.method == 'GET':
        return render_template('home/render_fileCSV.html')
    elif request.method == 'POST':
        file = request.files['file']
        df = pd.read_csv(file)
        return render_template('home/render_fileCSV.html', results=df.to_html())
    return render_template('home/render_fileCSV.html')


@blueprint.route('/bangsinhvien', methods=['GET', 'POST'])
def getStudent():
    column = ["No", "student code", "First name", "Last name", "DOB", "CN"]
    df = pd.read_csv('advanced_python.csv',  sep=";")
    df.columns = [column.replace(" ", "_") for column in df.columns]
    df.sort_values(by=['CN'])

    studentcode = request.form.get('search')
    if studentcode != "":
        result = df[df["student_code"] == studentcode]
        print(studentcode)
        return render_template('home/bangsinhvien.html', rows=result.iterrows())

    sort = request.form.get('sort')
    if sort == "A>>Z":
        result = df.sort_values(by=["Last_name"])
        return render_template('home/bangsinhvien.html', rows=result.iterrows())
    if sort == "Z>>A":
        result = df.sort_values(by=["Last_name"], ascending=False)
        return render_template('home/bangsinhvien.html', rows=result.iterrows())

    return render_template('home/bangsinhvien.html', rows=df.iterrows())


@blueprint.route('/admin')
def admin():
    entries = IncomeExpenses.query.order_by(IncomeExpenses.date.desc()).all()
    return render_template('transaction/main.html', entries=entries)


@blueprint.route('/admin/add', methods=["POST", "GET"])
def add_expense():
    form = UserDataForm()
    if form.validate_on_submit():
        entry = IncomeExpenses(
            type=form.type.data, category=form.category.data, amount=form.amount.data)
        db.session.add(entry)
        db.session.commit()
        flash(f"{form.type.data} has been added to {form.type.data}s", "success")

        return redirect("/admin")

    return render_template('transaction/add.html', title="Add expenses", form=form)

@blueprint.route('/deleteStudent/<id>')
def deleteStudent(id):
    mycursor.execute('DELETE FROM cs WHERE id = '+id+'')
    mydb.commit()
    return redirect(url_for('authentication_blueprint.lop'))

@blueprint.route('/xoaMonHoc/<id>')
def xoaMonHoc(id):
    mycursor.execute('DELETE FROM cs WHERE classCode = '+id+'')
    mydb.commit()

    mycursor.execute('DELETE FROM class WHERE id = '+id+'')
    mydb.commit()

    return redirect(url_for('authentication_blueprint.monhoc'))

@blueprint.route('/suamonhoc/<id>', methods = ['GET','POST'])
def suamonhoc(id):
     if request.method == 'GET':
        mycursor.execute('SELECT * FROM class WHERE id = '+id+'')
        tenmon = mycursor.fetchall()
        return render_template('home/suamonhoc.html', tenmon = tenmon)
     if request.method == 'POST':
        name = request.form.get("name")      
        mycursor.execute("UPDATE class SET name = '"+name+"'  WHERE id = '"+id+"'")
        mydb.commit()
        return redirect(url_for('authentication_blueprint.monhoc'))

@blueprint.route('/deletePost/<int:entry_id>')
def deletePost(entry_id):

    #entry = IncomeExpenses.query.get_or_404(int(entry_id))
    entry = db.session.query(IncomeExpenses).filter(
        IncomeExpenses.id == entry_id).first()
    db.session.delete(entry)
    db.session.commit()

    entries = IncomeExpenses.query.order_by(IncomeExpenses.date.desc()).all()
    return render_template('transaction/main.html', entries=entries)


@blueprint.route('admin/dashboard')
def dashboard():
    income_vs_expense = db.session.query(db.func.sum(IncomeExpenses.amount), IncomeExpenses.type).group_by(
        IncomeExpenses.type).order_by(IncomeExpenses.type).all()

    category_comparison = db.session.query(db.func.sum(IncomeExpenses.amount), IncomeExpenses.category).group_by(
        IncomeExpenses.category).order_by(IncomeExpenses.category).all()

    dates = db.session.query(db.func.sum(IncomeExpenses.amount), IncomeExpenses.date).group_by(
        IncomeExpenses.date).order_by(IncomeExpenses.date).all()

    income_category = []
    for amounts, _ in category_comparison:
        income_category.append(amounts)

    income_expense = []
    for total_amount, _ in income_vs_expense:
        income_expense.append(total_amount)

    over_time_expenditure = []
    dates_label = []
    for amount, date in dates:
        dates_label.append(date.strftime("%m-%d-%y"))
        over_time_expenditure.append(amount)

    return render_template('transaction/dashboard.html',
                           income_vs_expense=json.dumps(income_expense),
                           income_category=json.dumps(income_category),
                           over_time_expenditure=json.dumps(
                               over_time_expenditure),
                           dates_label=json.dumps(dates_label)
                           )


@blueprint.route('/User')
def User():
    return render_template('accounts/profile.html', user=current_user)
