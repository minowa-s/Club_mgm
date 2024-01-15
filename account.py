from curses import flash
from flask import Blueprint, redirect, render_template, request, session, url_for
import hashlib, string, random, psycopg2, db, os, bcrypt, datetime, smtplib
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
    session['department_id'] = department_id
    password = request.form.get('password') #パスワード
    session['password'] = request.form.get('password')
    password2 = request.form.get("password2") #再確認パスワード
    if password  == password2 :       
        return render_template('regist_conf.html', name=name, mail=mail, entrance_year=entrance_year, department_id=department_id)
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
    body = otp
    db.send_email(to_address, subject, body)
    return render_template('otp_send.html', otp=otp)
    

#アカウント登録
@account_bp.route('/regist_execute', methods=['POST'])
def regist_execute():
#     onetimepassword = request.form.get("otp")
#     name = session.get('name')
#     mail = session.get('mail')
#     entrance_year = session.get('entrance_year')
#     department_id = session.get('department_id')
#     department_id = str(department_id)
#     password = session.get('password')
#     salt = db.get_salt()    
#     print(salt, password)
#     hashed_password = db.get_hash(password, salt)
#     otp = session.get("otp")
#     if onetimepassword == otp:
#         sql = 'INSERT INTO student(name, mail, password, entrance_year, department_id, is_gakuseikai, onetimepassword, salt) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)' #name, mail,entrance_year, department,  hashedpassword, salt
#         try :
#             connection = get_connection()
#             cursor = connection.cursor()   
#             cursor.execute(sql, (name, mail, hashed_password, entrance_year, department_id, False, otp, salt))
#             connection.commit()
#         except psycopg2.DatabaseError:
#             count = 0
#         finally :
#             cursor.close()
#             connection.close()
#         return render_template('regist_execute.html', name=name, mail=mail, hashed_password=hashed_password, entrance_year=entrance_year, department_id=department_id, salt=salt, error=0)
#     else : return render_template('regist_execute.html', name=name, mail=mail, hashed_password=hashed_password, entrance_year=entrance_year, department_id=department_id, salt=salt, error=1)

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
            salt = db.get_salt()

            cursor.execute('INSERT INTO student(name, mail, password, entrance_year, department_id, is_gakuseikai, onetimepassword, salt) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)',
                           (name, mail, db.get_hash(password, salt), entrance_year, department_id, False, onetimepassword, salt))
            connection.commit()

            return render_template('regist_execute.html', name=name, mail=mail, hashed_password=db.get_hash(password, salt), entrance_year=entrance_year, department_id=department_id, salt=salt, error=0)

        except psycopg2.Error as e:
            print(f"データベースエラー: {e}")
            return render_template('regist_execute.html, name=name, mail=mail, hashed_password=hashed_password, entrance_year=entrance_year, department_id=department_id, salt=salt, error=1')

        finally:
            cursor.close()
            connection.close()

    return render_template('regist.html')        
# -----------------------------------------------------------------------------
# 教員アカウント関連

#アカウント登録
# アカウント登録画面
@account_bp.route('/tea_regist')
def tea_regist():
    return render_template('tea_regist.html')

# アカウント登録確認画面
@account_bp.route('/tea_regist_conf', methods=["POST"])
def tea_regist_conf():
    name = request.form.get('name')
    session['name'] = name
    mail = request.form.get('mail')
    mail['name'] = mail
    return render_template('tea_regist_conf.html', name=name, mail=mail)

#アカウント登録完了画面
@account_bp.route('/tea_regist_exe')
def tea_regist_exe():
    name = session.get('name')
    mail = session.get('mail')
    password = db.generate_pass()
    salt = db.get_salt()
    sql = 'INSERT INTO teacher(name, mail, password, first_pass_change, salt) VALUES(%s, %s, %s, %s, %s)' #name, mail,password, first_pass_change, salt
    try :
        connection = get_connection()
        cursor = connection.cursor()   
        cursor.execute(sql, (name, mail, password, False, salt))
        connection.commit()
    except psycopg2.DatabaseError:
        count = 0
    finally :
        cursor.close()
        connection.close()
    subject =  "教員用サークルアプリ" # ここにアカウント設定用のurlと現在のパスワード貼りたい
    body = "初期パスワード：" + "「" + password + "」"
    tea_account_regist_mail(mail, subject, body)
    return render_template('tea_regist_execute.html')


#登録したい教員アカウントにメールを送信する
def tea_account_regist_mail(to_address, subject, body):
    from_address = "h.nakamura.sys22@morijyobi.ac.jp" # 送信元と送信先のメールアドレス
    app_password = "lydt vxfw inil lffe"  # Gmailのアプリパスワードなどを使用してください
    # subject ="件名"
    # body ="本文"  URLを送る

    msg = MIMEMultipart()# メールの設定
    msg['From'] = from_address
    msg['To'] = to_address
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain')) # メール本文

    with smtplib.SMTP('smtp.gmail.com', 587) as server: # SMTPサーバーに接続してメールを送信
        server.starttls()
        server.login(from_address, app_password)
        server.sendmail(from_address, to_address, msg.as_string())


@account_bp.route('/tea_account_setting')
def tea_account_setting():
    nowpassword = request.form.get('nowpassword')
    newpassword = request.form.get('newpassword')
    newpassword2 = request.form.get('newpassword2')
    #パスワードの認証と新しいパスワードの誤字チェック    
    return render_template("tea_account_setting.html")

@account_bp.route('/tea_account_setting_conf', methods=['POST'])
def tea_account_setting_conf():
    return render_template("tea_account_setting_conf.html")

#-----------------------------------------------
#ログイン 
@account_bp.route('/login')
def login():
    return render_template('login/student_login.html')

#入力後の画面遷移
@account_bp.route('/student_login_exe', methods=['POST'])
# def student_login_exe():
#     mail = request.form.get('mail')
#     print(mail)
#     password = request.form.get('password')
#     print(password)
#     #データベースからソルト取得
#     salt = get_account_salt(mail)
#     print(type(salt))
#     #入力されたパスワードをハッシュ化
#     hashed_password = db.get_hash("test", salt)
#     print(hashed_password)
#     #データベースからパスワードとソルト取得
#     passw = get_account_pass(mail)
#     if  hashed_password == passw :
#         #成功でホーム画面
#         return render_template('top_stu.html', passw=passw, error='成功')
#     else :
#         return render_template('login/student_login.html', passw=passw, error='失敗')
def student_login_exe():
    if request.method == 'POST':
        mail = request.form.get('mail')
        password = request.form.get('password')

        # データベースからソルトを取得
        salt = get_account_salt(mail)

        if salt is not None:
            # パスワードとソルトを使ってハッシュを生成
            hashed_password = db.get_hash(password, salt)
            print("hashed=", hashed_password)
            # データベースから保存されたハッシュを取得
            stored_password = get_account_pass(mail)
            print("stored=", stored_password)
            # ハッシュが一致すればログイン成功
            if hashed_password == stored_password:
                session['mail'] = mail  # セッションにユーザー情報を保存
                return render_template('top_stu.html')
            else:
                print('Invalid mail or password')
                return render_template('login/student_login.html')
        else:
            print('Invalid mail or password')
            return render_template('login/student_login.html')

    return render_template('login/student_login.html')

@account_bp.route('/home')
def move_home():
    return render_template('admin_home.html')

@account_bp.route('/index', methods=['POST'])
def move_index():
    return render_template('login/login.html')

def login_process():
    sql = 'SELECT * FROM student WHERE mail = %s AND password = %s'
    mail = request.form.get('mail')
    password = request.form.get('password')
    
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql, (mail, password))
        user = cursor.fetchone()
             
    except psycopg2.DatabaseError:
        flg = False
    finally:
        cursor.close()
        connection.close()
    return flg


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
        print("get_account_pass", str_pw)
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
        print("get_account_salt:" , str_salt)
    return str_salt