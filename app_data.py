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

@app_data_bp.route('/get_request_exe')
def get_request_exe():
    club_id = request.args.get('club_id')
    request_detail = db.get_club_dedtail(club_id)
    leader_mail = get_leader(request_detail[1])
    #サークルに入っている学生のメールアドレスを取得
    student_ids = db.get_student_id_from_student_club(club_id)
    #student_mails = db.get_student_mail(student_ids)
    print(student_ids)
    return render_template('request.detail.html', request_detail=request_detail, leader_mail=leader_mail)

#申請ありサークルリスト表示
def select_allow0_club():
    #リーダーidを取得
    sql = "SELECT * FROM club WHERE allow = 0"
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

if __name__ == '__main__':
    app.run(debug=True)