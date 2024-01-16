import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import hashlib
import os, psycopg2
import string
import random
import smtplib

def get_connection():
    url = os.environ['DATABASE_URL']
    connection = psycopg2.connect(url)
    return connection

#ハッシュ取得
# def get_hash(password, salt):
#     b_pw = bytes(password, 'utf-8')
#     b_salt = bytes(salt, 'utf-8')
#     hashed_password = hashlib.pbkdf2_hmac('sha256', b_pw, b_salt, 200).hex()
#     return hashed_password
    #------------
def get_hash(password, salt):
    # 文字列をバイト列に変換
    b_password = bytes(password, 'utf-8')
    b_salt = bytes(salt, 'utf-8')
    # PBKDF2_HMAC イテレーション数: 200, ハッシュアルゴリズム: SHA-256
    hashed_password = hashlib.pbkdf2_hmac('sha256', b_password, b_salt, 200).hex()
    return hashed_password
#------------

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

#ソルト生成
def get_salt():
    charset = string.ascii_letters + string.digits
    salt = '' .join(random.choices(charset, k=30))
    return salt

#パスワード生成(教員初期ぱすわーど)
def generate_pass():
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(8))
    return random_string
        
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

#サークル立ち上げ申請
def request_club(club_name, leader_mail, objective, activities, introduction, note):
    sql = 'INSERT INTO club VALUES (default, %s, %s, %s, %s, %s, %s, 0)'
    try : # 例外処理
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql, (club_name, leader_mail, objective, activities, introduction, note))
        count = cursor.rowcount # 更新件数を取得
        connection.commit()
    except psycopg2.DatabaseError: # Java でいうcatch 失敗した時の処理をここに書く
        count = 0 # 例外が発生したら0 をreturn する。
    finally: # 成功しようが、失敗しようが、close する。
        cursor.close()
        connection.close()
    return count

def get_request_club():
    connection = get_connection()
    cursor = connection.cursor()
    sql = "SELECT name, leader_id, objective, activities, introduction FROM club where name = 'Python開発サークル'"
    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return rows

#サークル詳細
def get_club_dedtail(club_id):
    connection = get_connection()
    cursor = connection.cursor()
    sql = "SELECT name, leader_id, objective, activities, introduction, note FROM club where club_id = %s"
    cursor.execute(sql, (club_id,))
    rows = cursor.fetchone()
    cursor.close()
    connection.close()
    return rows

#サークル立ち上げ申請に入っている学生idの取得
def get_student_id_from_student_club(club_id):
    connection = get_connection()
    cursor = connection.cursor()
    sql = "SELECT student_id FROM student_club where club_id = %s and is_leader = False"
    cursor.execute(sql, (club_id,))
    student_id_list = cursor.fetchall()
    cursor.close()
    connection.close()
    return student_id_list

def get_student_mail(student_id):
    connection = get_connection()
    cursor = connection.cursor()
    sql = "SELECT mail FROM student WHERE student_id = %s"
    cursor.execute(sql, (student_id,))
    student_mail = cursor.fetchone()
    cursor.close()
    connection.close()
    return student_mail
#=========================================================
#サークル否認
def delete_request(club_id):
    delete_from_student_club(club_id)
    sql = "DELETE FROM club WHERE club_id = %s"
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(sql, (club_id,))
    connection.commit()
    cursor.close()
    connection.close()
    
#サークル消す前にs_tテーブルを削除
def delete_from_student_club(club_id):
    sql = "DELETE FROM student_club WHERE club_id = %s"
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(sql, (club_id,))
    connection.commit()
    cursor.close()
    connection.close()
    
#---------------------------------------------------
#サークル削除（リーダーが消す）
def delete_club(club_id):
    sql = "INSERT INTO club_delete(club_id, delete_request_time) VALUES(%s, now())"
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(sql, (club_id))
    connection.commit()
    cursor.close()
    connection.close
#-----学生会登録--------------------------------------------
#メールアドレスから学生が存在するかの検索、名前の取得
def student_seach_from_mail(mail):
    sql = "SELECT name, mail FROM student WHERE mail = %s"
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(sql, (mail,))
    list = cursor.fetchone()
    cursor.close()
    connection.close()
    return list

def gakuseikai_regist(mail):
    sql = "UPDATE student SET is_gakuseikai = True WHERE mail = %s"
    connection = get_connection()
    cursor = connection.cursor()   
    cursor.execute(sql, (mail,))
    connection.commit()
    cursor.close()
    connection.close()
    
#メール送信
def mail_send(to_address, subject, body):
    from_address = "h.nakamura.sys22@morijyobi.ac.jp" # 送信元と送信先のメールアドレス
    app_password = "lydt vxfw inil lffe"  # Gmailのアプリパスワードなどを使用してください
    # subject ="件名"
    # body ="本文"  

    msg = MIMEMultipart()# メールの設定
    msg['From'] = from_address
    msg['To'] = to_address
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain')) # メール本文

    with smtplib.SMTP('smtp.gmail.com', 587) as server: # SMTPサーバーに接続してメールを送信
        server.starttls()
        server.login(from_address, app_password)
        server.sendmail(from_address, to_address, msg.as_string())

#リーダーid取得
def get_leader():
    sql = "SELECT student_id FROM student_club WHERE is_leader = true"
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(sql)
    leader_list = []
    for row in cursor.fetchall():
        leader_list.append((row[0])) #row[0]=student_id,
    cursor.close()
    connection.close()
    return leader_list