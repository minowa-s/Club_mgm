from flask import Flask, Blueprint, render_template, request, redirect, url_for, session
import db, string, random, os, psycopg2
from datetime import timedelta

app = Flask(__name__)
app.secret_key = ''.join(random.choices(string.ascii_letters, k=256))
app_data_bp = Blueprint('app_data', __name__, url_prefix='/app_data')

#DB接続
def get_connection():
    url = os.environ['DATABASE_URL']
    connection = psycopg2.connect(url)
    return connection

#サークル立ち上げ申請リスト
@app_data_bp.route('/approve_list_te')
def approve_list_te():
    club_list = select_allow1_club()
    return render_template('approve_list/approve_list_te.html', club_list=club_list)

#サークル立ち上げ申請確認
@app_data_bp.route('/get_request_conf')
def get_request_conf():
    club_id = request.args.get('club_id')
    request_detail = db.get_club_detail(club_id)
    leader_mail = get_leader(request_detail[1])
    #サークルに入っている学生のメールアドレスを取得
    student_ids = list(db.get_student_id_from_student_club(club_id))
    count = 0
    student_mail_list = []
    for row in student_ids :
        student_mail = db.get_student(student_ids[count])
        student_mail_list.append(student_mail[2])
        count+= 1
    return render_template('club_create/request.detail.html', request_detail=request_detail, leader_mail=leader_mail, student_mail_list=student_mail_list, club_id=club_id)

#サークル立ち上げ承認
@app_data_bp.route('/request_exe', methods=['POST'])
def request_exe():
    club_id = request.form.get('club_id')
    update_club(club_id)
    club = db.get_club_detail(club_id)
    update_leader_flg(club[1])
    update_member_allow(club_id)
    return render_template('club_create/create_exe.html')
    
#サークル立ち上げ拒否
@app_data_bp.route('/club_not_create', methods=['POST'])
def club_not_create():
    club_id = request.form.get('club_id')
    session['club_id'] = club_id
    return render_template('club_create/club_not_create.html', club_id=club_id)

#サークル立ち上げ否認理由確認
@app_data_bp.route('/club_not_create_conf', methods=['POST'])
def club_not_create_conf():
    reason = request.form.get('reason')
    return render_template('club_create/club_not_create_conf.html', reason=reason)

#サークル立ち上げ否認確定
@app_data_bp.route('/club_not_create_exe')
def club_not_create_exe():
    club_id = session.get('club_id')
    db.delete_request(club_id)
    return render_template('club_create/club_not_create_exe.html')

#学生会登録
@app_data_bp.route('/gakuseikai_regist')
def gakuseikai_regist():
    return render_template('gakuseikai_regist/gakuseikai_regist.html')

#学生会登録
@app_data_bp.route('/gakuseikai_regist_conf', methods=['POST'])
def gakuseikai_regist_conf():
    mails = request.form.get('mail')
    mails = mails.splitlines()
    mail_list = []
    for row in mails:
        mail = db.student_seach_from_mail(row)
        mail_list.append(mail)
    print("conf____maillist")
    print(mail_list)
    print("conf____mails")
    session['mails'] = mails
    return render_template('gakuseikai_regist/gakuseikai_regist_conf.html', mail_list=mail_list, mails=mails)

@app_data_bp.route('/gakuseikai_regist_exe')
def gakuseikai_regist_exe():
    mails = session.get('mails')
    mail_list = request.args.get('mails')
    mail_list = mail_list.splitlines()
    mail_list = []
    for row in mails:
        mail = db.gakuseikai_regist(row)
        mail_list.append(mail)
        db.gakuseikai_regist(row)
    return render_template('gakuseikai_regist/gakuseikai_regist_exe.html')

    
#申請ありサークルリスト表示
def select_allow1_club():
    #リーダーidを取得
    sql = "SELECT * FROM club WHERE allow = 1"
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(sql)
    club_list = []
    for row in cursor.fetchall():
        leader = get_leader(row[2])
        print(leader)
        year = get_leader(row[2])
        department = get_department(leader[5])
        club_list.append((row[0], row[1], leader[1], department[1], year[4])) #row[0]=club_id, row[1]=club_name
    cursor.close()
    connection.close()
    return club_list

#reader_idからリーダーの情報を取得
def get_leader(student_id):
    sql = "SELEcT * FROM student WHERE student_id = %s"
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(sql, (student_id,))
    leader = cursor.fetchone()
    cursor.close()
    connection.close()
    return leader


#department_idからdepartment_name取得
def get_department(department_id):
    sql = "SELEcT * FROM department WHERE department_id = %s"
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(sql, (department_id,))
    department = cursor.fetchone()
    cursor.close()
    connection.close()
    return department

#サークル承認（教員）
def update_club(club_id):
    print(club_id)
    sql = "UPDATE club SET allow = 2 WHERE club_id = %s"
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(sql, (club_id,))
    connection.commit()
    cursor.close()
    connection.close()
    
#サークル承認(リーダーフラグ変更)
def update_leader_flg(student_id):
    print(student_id)
    sql = "UPDATE student_club SET is_leader = True, allow = 1 WHERE student_id = %s"
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(sql, (student_id,))
    connection.commit()
    cursor.close()
    connection.close()#サークル承認(リーダーフラグ変更)
    
def update_member_allow(club_id):
    sql = "UPDATE student_club SET allow = 1 WHERE club_id = %s"
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(sql, (club_id,))
    connection.commit()
    cursor.close()
    connection.close()

#サークル削除
@app_data_bp.route('/club_delete', methods=['POST'])
def club_delete():
    club_id = request.form.get('club_id')
    session['club_id'] = club_id
    return render_template('club_delete.html')

#サークル削除確認
@app_data_bp.route('club_delete_conf')
def club_delete_conf():
    club_id = session.get('club_id')
    db.delete_club(club_id)
    print('A')
    return render_template('club_delete_request_exe.html')

#----------------メール送信
@app_data_bp.route('mail_send')
def mail_send():
    return render_template('mail_send.html')

@app_data_bp.route('mail_send_conf', methods=['POST'])
def mail_send_conf():
    subject = request.form.get('subject')
    body = request.form.get('body')
    leader_id_list = db.get_leader()
    print(leader_id_list)
    for row in leader_id_list:
        leader = get_leader(row)
        db.mail_send(leader[2], subject, body)
    return render_template('mail_send_conf.html')
   
if __name__ == '__main__':
    app.run(debug=True)