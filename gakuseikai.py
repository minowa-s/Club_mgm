from flask import Flask, Blueprint, render_template, request, redirect, url_for, session
import db, string, random, os, psycopg2, app_data
from datetime import timedelta

app = Flask(__name__)
app.secret_key = ''.join(random.choices(string.ascii_letters, k=256))
gakuseikai_bp = Blueprint('gakuseikai', __name__, url_prefix='/gakuseikai')

#DB接続
def get_connection():
    url = os.environ['DATABASE_URL']
    connection = psycopg2.connect(url)
    return connection

#サークル立ち上げ申請リスト
@gakuseikai_bp.route('/approve_list_st')
def approve_list_st():
    club_list = select_allow0_club()
    return render_template('approve_list/approve_list_st.html', club_list=club_list)

#サークル立ち上げ申請確認
@gakuseikai_bp.route('/get_request_conf')
def get_request_conf():
    club_id = request.args.get('club_id')
    request_detail = db.get_club_detail(club_id)
    leader_mail = app_data.get_leader(request_detail[1])
    #サークルに入っている学生のメールアドレスを取得
    student_ids = list(db.get_student_id_from_student_club(club_id))
    count = 0
    student_mail_list = []
    for row in student_ids :
        student_mail = db.get_student(student_ids[count])
        student_mail_list.append(student_mail[2])
        count+= 1
    return render_template('club_create/request.detailG.html', request_detail=request_detail, leader_mail=leader_mail, student_mail_list=student_mail_list, club_id=club_id)

#サークル立ち上げ承認
@gakuseikai_bp.route('/request_exe', methods=['POST'])
def request_exe():
    club_id = request.form.get('club_id')
    app_data.update_club(club_id)
    return render_template('club_create/request_exe.html')
    
#サークル立ち上げ拒否
@gakuseikai_bp.route('/club_not_create', methods=['POST'])
def club_not_create():
    club_id = request.form.get('club_id')
    session['club_id'] = club_id
    return render_template('club_create/club_not_create.html', club_id=club_id)

#サークル立ち上げ否認理由確認
@gakuseikai_bp.route('/club_not_create_conf', methods=['POST'])
def club_not_create_conf():
    reason = request.form.get('reason')
    return render_template('club_create/club_not_create_conf.html', reason=reason)

@gakuseikai_bp.route('/club_not_create_exe')
def club_not_create_exe():
    club_id = session.get('club_id')
    db.delete_request(club_id)
    return render_template('club_create/club_not_create_exe.html')


#申請ありサークルリスト表示
def select_allow0_club():
    #リーダーidを取得
    sql = "SELECT * FROM club WHERE allow = 0"
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(sql)
    club_list = []
    for row in cursor.fetchall():
        leader_name = app_data.get_leader(row[2])
        year = app_data.get_leader(row[2])
        department = app_data.get_department(row[2])
        club_list.append((row[0], row[1], leader_name[1], department[1], year[4])) #row[0]=club_id, row[1]=club_name
    cursor.close()
    connection.close()
    return club_list

