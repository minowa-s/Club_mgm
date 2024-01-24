import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import hashlib
import os, psycopg2
import string
import random
import smtplib

#DB接続
def get_connection():
    url = os.environ['DATABASE_URL']
    connection = psycopg2.connect(url)
    return connection

#ソルト取得
def get_account_salt(mail):
    sql = 'SELECT salt FROM teacher WHERE mail = %s'
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

#パスワード取得
def get_account_pass(mail):
    sql = 'SELECT password FROM teacher WHERE mail = %s'
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

def login(mail, password):  
    print(mail, password)
    sql='SELECT password, salt FROM teacher WHERE mail = %s'
    flg=False
    try : 
        connection=get_connection()
        cursor=connection.cursor()
        cursor.execute(sql, (mail,))
        user=cursor.fetchone()
        print('rgw')
        if user!=None:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            print(hashed_password)
            # 生成したハッシュ値とDBから取得したハッシュ値を比較する
            if hashed_password==user[0]:
                flg=True
    except psycopg2.DatabaseError:
        print('DBerror')
        flg=False
    finally:
        cursor.close()
        connection.close()
    return flg

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

