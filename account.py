from flask import Blueprint, render_template, request, session
import hashlib, string, random, psycopg2, os, bcrypt, datetime, smtplib
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
    department = select_department()
    year = select_year()
    return render_template('regist.html', department=department, year=year)

#アカウント登録情報確認
@account_bp.route('/regist_conf', methods=['POST'])
def regist_conf():
    name = request.form.get('name')
    session['name'] = name
    mail = request.form.get('mail')
    session['mail'] = mail
    entrance_year = request.form.get('entrance_year')
    session['entrance_year'] = entrance_year
    department_id = request.form.get('department')
    session['department_id'] = department_id
    password = request.form.get('password')
    session['password'] = request.form.get('password')
    salt = get_salt()
    hashed_password = hash_password(password)
    password2 = request.form.get("password2")
    if password  == password2 :       
        return render_template('regist_conf.html', name=name, mail=mail, hashed_password=hashed_password, entrance_year=entrance_year, department_id=department_id, salt=salt)
    else :
        department = select_department()
        year = select_year()
        return render_template('regist.html', name=name, mail=mail,department=department, year=year)
#ワンタイムパスワード入力画面
@account_bp.route('/otp_send', methods=['POST'])
def otp_send():
    mail = request.form.get("mail")
    to_address = mail
    otp = generate_otp()
    session["otp"] = otp
    subject =  "サークルアプリワンタイムパスワード"
    body = otp
    send_email(to_address, subject, body)
    return render_template('otp_send.html', otp=otp)
    

#アカウント登録
@account_bp.route('/regist_execute', methods=['POST'])
def regist_execute():
    onetimepassword = request.form.get("otp")
    name = session.get('name')
    mail = session.get('mail')
    entrance_year = session.get('entrance_year')
    department_id = session.get('department_id')
    department_id = str(department_id)
    print(entrance_year, department_id)
    password = session.get('password')
    salt = get_salt()
    hashed_password = get_hash(password, salt)
    otp = session.get("otp")
    if onetimepassword == otp:
        sql = 'INSERT INTO student(name, mail, password, entrance_year, department_id, is_gakuseikai, onetimepassword, salt) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)' #name, mail,entrance_year, department,  hashedpassword, salt
        try :
            connection = get_connection()
            cursor = connection.cursor()   
            cursor.execute(sql, (name, mail, hashed_password, entrance_year, department_id, False, otp, salt))
            connection.commit()
        except psycopg2.DatabaseError:
            count = 0
        finally :
            cursor.close()
            connection.close()
        return render_template('regist_execute.html', name=name, mail=mail, hashed_password=hashed_password, entrance_year=entrance_year, department_id=department_id, salt=salt, error=0)
    else : return render_template('regist_execute.html', name=name, mail=mail, hashed_password=hashed_password, entrance_year=entrance_year, department_id=department_id, salt=salt, error=1)

# ワンタイムパスワード取得
def select_otp(mail):
    sql = "SELECT onetimepassword from student WHERE mail = %s"
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql, (mail,))
        passw = cursor.fetchone() 
        
    except psycopg2.DatabaseError:
        flg = False
    finally:
        cursor.close()
        connection.close()
        
    return passw

#アカウントパスワード取得
def get_account_pass(mail):
    sql = 'SELECT password FROM users WHERE mail = %s'
    
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

#アカウントソルト取得
def get_account_salt(mail):
    sql = 'SELECT salt FROM users WHERE mail = %s'
    
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

#ソルト取得
def get_salt():
    charset = string.ascii_letters + string.digits
    salt = '' .join(random.choices(charset, k=30))
    return salt

#ハッシュ取得
def get_hash(password, salt):
    b_pw = bytes(password, 'utf-8')
    b_salt = bytes(salt, 'utf-8')
    hashed_password = hashlib.pbkdf2_hmac('sha256', b_pw, b_salt, 200).hex()
    return hashed_password

    # パスワードをハッシュ化
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password
        
# ワンタイムパスワード取得    
def generate_otp():
    # 6桁のランダムな数字を生成
    otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    return otp

# 学科取得（登録時に選択でだすやつ）
def select_department():
    sql = "SELECT * FROM department"
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(sql)
    department_list = []
    for row in cursor.fetchall():
        department_list.append((row[0], row[1]))
    connection.close()
    return department_list

#入学年度選択
def select_year():
    current_year = datetime.datetime.now().year
    year_range = range(current_year, current_year - 4, -1)
    return year_range

#メール送信 
def send_email(to_address, subject, body):
    # 送信元と送信先のメールアドレス
    from_address = "h.nakamura.sys22@morijyobi.ac.jp"
    app_password = "lydt vxfw inil lffe"  # Gmailのアプリパスワードなどを使用してください

    # メールの設定
    msg = MIMEMultipart()
    msg['From'] = from_address
    msg['To'] = to_address
    msg['Subject'] = subject

    # メール本文
    msg.attach(MIMEText(body, 'plain'))

    # SMTPサーバーに接続してメールを送信
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(from_address, app_password)
        server.sendmail(from_address, to_address, msg.as_string())
        
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
@account_bp.route('/tea_regist_exe', methods=["POST"])
def tea_regist_exe():
    name = session.get('name')
    mail = session.get('mail')
    tea_account_regist_mail(mail)
    return render_template('tea_regist_exe.html')

#登録したい教員アカウントにメールを送信する
def tea_account_regist_mail(to_address):
    from_address = "h.nakamura.sys22@morijyobi.ac.jp" # 送信元と送信先のメールアドレス
    app_password = "lydt vxfw inil lffe"  # Gmailのアプリパスワードなどを使用してください
    subject ="件名"
    body ="本文" # URLを送る

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
def account_setting():
    password = request.form.get('password')

