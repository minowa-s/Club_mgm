
from flask import Blueprint, redirect, render_template, request, session, url_for
import hashlib, string, random, psycopg2, db, os, bcrypt, datetime, admin_db
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

#DB接続
def get_connection():
    url = os.environ['DATABASE_URL']
    connection = psycopg2.connect(url)
    return connection

@admin_bp.route('/tea_regist')
def tea_regist():
    return render_template('tea_regist.html')

# アカウント登録確認画面
@admin_bp.route('/tea_regist_conf', methods=["POST"])
def tea_regist_conf():
    name = request.form.get('name')
    session['name'] = name
    mail = request.form.get('mail')
    mail['name'] = mail
    return render_template('tea_regist_conf.html', name=name, mail=mail)

#アカウント登録完了画面
@admin_bp.route('/tea_regist_exe')
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
    admin_bp.tea_account_regist_mail(mail, subject, body)
    return render_template('tea_regist_execute.html')

#ログイン
@admin_bp.route('/login')
def login():
    return render_template('admin/login.html')

#入力後の画面遷移
@admin_bp.route('/login_exe', methods=['POST'])
def login_exe():
    mail = request.form.get('mail')
    password = request.form.get('password')
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    print(hashed_password)
    #データベースからソルト取得
    salt = admin_db.get_account_salt(mail)
    if salt is not None:
            # パスワードとソルトを使ってハッシュを生成
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            # データベースから保存されたハッシュを取得
            stored_password = admin_db.get_account_pass(mail)
            print(stored_password)
            print(password)
            # ハッシュが一致すればログイン成功
            if admin_db.login(mail, password) == True:
                session['mail'] = mail  # セッションにユーザー情報を保存
                return render_template('top/top_teacher.html')
            else:
                print('Invalid password')
                return render_template('admin/login.html')
    else:
        print('Invalid mail ')
        return render_template('admin/login.html')

#アカウントセッティング    
@admin_bp.route('/tea_account_setting')
def tea_account_setting():
    nowpassword = request.form.get('nowpassword')
    newpassword = request.form.get('newpassword')
    newpassword2 = request.form.get('newpassword2')
    #パスワードの認証と新しいパスワードの誤字チェック    
    return render_template("tea_account_setting.html")

#アカウントセッティング確認画面
@admin_bp.route('/tea_account_setting_conf', methods=['POST'])
def tea_account_setting_conf():
    return render_template("tea_account_setting_conf.html")

#アカウント管理画面へ
@admin_bp.route('/account_mgm_top')
def account_mgm_top():
    return render_template("admin/account_mgm/account_mgm_top.html")
