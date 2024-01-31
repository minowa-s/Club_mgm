from flask import Blueprint, redirect, render_template, request, session, url_for
import hashlib, string, random, psycopg2, db, os, bcrypt, datetime, smtplib, club, app_data
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

account_bp = Blueprint('account', __name__, url_prefix='/account')

#DB接続
def get_connection():
    url = os.environ['DATABASE_URL']
    connection = psycopg2.connect(url)
    return connection

# アカウント登録画面
@account_bp.route('/regist')
def regist():
    department = db.select_department()
    year = db.select_year()
    print(year)
    return render_template('regist.html', department=department, year=year)

#アカウント登録情報確認
@account_bp.route('/regist_conf', methods=['POST'])
def regist_conf():
    name = request.form.get('name') #氏名
    session['name'] = name
    mail = request.form.get('mail') #メールアドレス
    session['mail'] = mail
    entrance_year = request.form.get('entrance_year') #入学年度
    session['entrance_year'] = entrance_year
    department_id = request.form.get('department') #学科
    department = app_data.get_department(department_id)
    department_name = department[1]
    session['department_id'] = department_id
    password = request.form.get('password') #パスワード
    session['password'] = request.form.get('password')
    password2 = request.form.get("password2") #再確認パスワード
    if password  == password2 :       
        return render_template('regist_conf.html', name=name, mail=mail, entrance_year=entrance_year, department_name=department_name)
    else :
        department = db.select_department()
        year = db.select_year()
        return render_template('regist.html', name=name, mail=mail,department=department, year=year)

#ワンタイムパスワード入力画面
@account_bp.route('/otp_send', methods=['POST'])
def otp_send():
    mail = request.form.get("mail")
    to_address = mail
    otp = db.generate_otp()
    session["otp"] = otp
    subject =  "サークルアプリワンタイムパスワード"
    body = "ワンタイムパスワード：" , otp
    db.send_email(to_address, subject, body)
    return render_template('otp_send.html', otp=otp)
    

#アカウント登録
@account_bp.route('/regist_execute', methods=['POST'])
def regist_execute():
    if request.method == 'POST':
        onetimepassword = request.form.get("otp")
        name = session.get('name')
        mail = session.get('mail')
        entrance_year = session.get('entrance_year')
        department_id = session.get('department_id')
        department_id = str(department_id)
        password = session.get('password')

        # データベースに接続してユーザーの重複を確認
        connection = get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute('SELECT * FROM student WHERE mail = %s', (mail,))
            existing_user = cursor.fetchone()

            if existing_user:
                return render_template('regist_execute.html')

            # 新しいユーザーをデータベースに追加
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            salt = "a"
            cursor.execute('INSERT INTO student(name, mail, password, entrance_year, department_id, is_gakuseikai, onetimepassword, salt) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)',
                           (name, mail, hashed_password, entrance_year, department_id, False, onetimepassword, salt))
            connection.commit()

            return render_template('regist_execute.html', name=name, mail=mail, hashed_password=db.get_hash(password, salt), entrance_year=entrance_year, department_id=department_id, salt=salt, error=0)

        except psycopg2.Error as e:
            print(f"データベースエラー: {e}")
            return render_template('regist_execute.html', name=name, mail=mail, hashed_password=hashed_password, entrance_year=entrance_year, department_id=department_id, salt=salt, error=1)

        finally:
            cursor.close()
            connection.close()

    return render_template('regist.html')        
#-----------------------------------------------
#ログイン 
@account_bp.route('/login')
def login():
    return render_template('login/student_login.html')

#入力後の画面遷移
@account_bp.route('/student_login_exe', methods=['POST'])
def student_login_exe():
    mail = request.form.get('mail')
    password = request.form.get('password')
    #データベースからソルト取得
    salt = get_account_salt(mail)
    if salt is not None:
            # パスワードとソルトを使ってハッシュを生成
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            # データベースから保存されたハッシュを取得
            stored_password = get_account_pass(mail)
            session['mail'] = mail
            # ハッシュが一致すればログイン成功
            if hashed_password == stored_password:
                id = db.get_id(mail)
                student = db.get_student(id)
                club_list = club.club_list()
                leader = db.get_sc(id)
                print(leader)
                print("aaa")
                gakuseikai = db.get_student(id)

                #リーダー判定
                if leader is not None and leader[3] == True and leader[4] == 1:    
                    return render_template('top/top_leader.html', club_list=club_list, student=student[0])
                else:
                    if gakuseikai[6] == True :
                        return render_template('top/top_council.html', club_list=club_list, student=student)
                    print(student)
                    return render_template('top/top_student.html', club_list=club_list, student=student)
            else:
                print('Invalid mail or password')
                return render_template('login/student_login.html')
    else:
        print('Invalid mail or password')
        return render_template('login/student_login.html')
    
#------------------------------
#ログアウト
@account_bp.route('logout')
def logout():
    club_list = club.club_list()
    return render_template('top/top.html', club_list=club_list)

#パスワード取得
def get_account_pass(mail):
    sql = 'SELECT password FROM student WHERE mail = %s'
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql, (mail,))
        passw = cursor.fetchone()
        str_pw = str(passw[0])
    except psycopg2.DatabaseError:
        flg = False
    finally:
        cursor.close()
        connection.close()
    return str_pw

#ソルト取得
def get_account_salt(mail):
    sql = 'SELECT salt FROM student WHERE mail = %s'
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql, (mail,))
        salt = cursor.fetchone()
        str_salt = str(salt[0])
    except psycopg2.DatabaseError:
        flg = False
    finally:
        cursor.close()
        connection.close()
    return str_salt

#-----------------------------
#パスワード変更
@account_bp.route('/password_reset')
def password_reset():
    return render_template('password_reset/password_reset1.html')

@account_bp.route('/password_reset2', methods=['POST'])
def password_reset2():
    mail = request.form.get('mail')
    student = mail_confirm(mail)
    session['student'] = student
    if student != False :
        otp = db.generate_otp()
        print(student)
        insert_otp(student[0], otp)
        db.send_email(mail, "パスワード再設定用ワンタイムパスワード", otp)
        return render_template('password_reset/password_reset2.html')
    else :
        return render_template('password_reset/password_reset1.html' , flg=False)
    
@account_bp.route('/password_reset3', methods=['POST'])
def password_reset3():
    otp = int(request.form.get("otp"))
    student = session.get('student')
    selected_otp = select_otp(student[0])
    selected_otp = int("".join(map(str, selected_otp)))
    if otp == selected_otp :
        session["otp"] = otp
        session["student"] = student[0]
        delete_otp(student[0])
        return render_template("password_reset/password_reset3.html")
    return render_template('password_reset/password_reset2.html', error=1)

@account_bp.route('/password_reset4', methods=['POST'])
def password_reset4():
    pass1 = request.form.get("pass1")
    pass2 = request.form.get('pass2')
    student_id = session.get("student")
    if pass1 != pass2 :
        return render_template("password_reset/password_reset3.html", error=1)
    print(student_id)
    hashed_pass = hashlib.sha256(pass1.encode()).hexdigest()
    print(hashed_pass)
    update_pass(student_id, hashed_pass)
    return render_template('password_reset/password_reset_exe.html')
    
def mail_confirm(mail):
    sql = "SELECT * FROM student WHERE mail = %s"
    try :
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql, (mail,))
        student = cursor.fetchone()
    except psycopg2.DatabaseError:
        student = False
    finally:
        cursor.close()
        connection.close()
    return student

def insert_otp(student_id, otp):
    sql = "INSERT INTO stu_pass_reset VALUES(%s, %s, now())"
    try :
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql, (student_id, otp))
        connection.commit()
    except psycopg2.DatabaseError:
        student = False
    finally:
        cursor.close()
        connection.close()
        
def select_otp(student_id):
    sql = "select onetimepassword from stu_pass_reset where student_id = %s"
    try :
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql, (student_id,))
        otp = cursor.fetchone()
    except psycopg2.DatabaseError:
        otp = False
    finally:
        cursor.close()
        connection.close()
    return otp

def delete_otp(student_id):
    sql = "delete * from stu_pass_reset where student_id = %s"
    try :
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql, (student_id,))
        otp = cursor.fetchone()
    except psycopg2.DatabaseError:
        otp = False
    finally:
        cursor.close()
        connection.close()
    return otp

def update_pass(student_id, password):
    sql = "UPDATE student SET password = %s WHERE student_id = %s"
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(sql, (password, student_id))
    connection.commit()
    cursor.close()
    connection.close()