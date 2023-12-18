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
@app_data_bp.route('/approve_list_st')
def approve_list_st():
    club_list = select_allow0_club()
    return render_template('approve_list_te.html', club_list=club_list)

#サークル立ち上げ申請確認
@app_data_bp.route('/get_request_conf')
def get_request_conf():
    club_id = request.args.get('club_id')
    request_detail = db.get_club_dedtail(club_id)
    leader_mail = get_leader(request_detail[1])
    #サークルに入っている学生のメールアドレスを取得
    student_ids = list(db.get_student_id_from_student_club(club_id))
    count = 0
    student_mail_list = []
    for row in student_ids :
        student_mail = db.get_student_mail(student_ids[count])
        student_mail_list.append(student_mail)
        count+= 1
    return render_template('request.detail.html', request_detail=request_detail, leader_mail=leader_mail, student_mail_list=student_mail_list, club_id=club_id)

#サークル立ち上げ承認
@app_data_bp.route('/request_exe', methods=['POST'])
def request_exe():
    club_id = request.form.get('club_id')
    update_club(club_id)
    return render_template('request_exe.html')
    
#サークル立ち上げ拒否
@app_data_bp.route('/club_not_create', methods=['POST'])
def club_not_create():
    club_id = request.form.get('club_id')
    session['club_id'] = club_id
    return render_template('club_not_create.html', club_id=club_id)

#サークル立ち上げ否認理由確認
@app_data_bp.route('/club_not_create_conf', methods=['POST'])
def club_not_create_conf():
    reason = request.form.get('reason')
    return render_template('club_not_create_conf.html', reason=reason)

@app_data_bp.route('/club_not_create_exe')
def club_not_create_exe():
    club_id = session.get('club_id')
    db.delete_request(club_id)
    return render_template('club_not_create_exe.html')


    
#申請ありサークルリスト表示
def select_allow0_club():
    #リーダーidを取得
    sql = "SELECT * FROM club WHERE allow = 1"
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(sql)
    club_list = []
    for row in cursor.fetchall():
        leader_name = get_leader(row[2])
        year = get_leader(row[2])
        department = get_department(row[2])
        club_list.append((row[0], row[1], leader_name[1], department[1], year[4])) #row[0]=club_id, row[1]=club_name
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


if __name__ == '__main__':
    app.run(debug=True)