from flask import Blueprint, Flask, render_template, request, session
import db, club

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # セッション管理のための秘密鍵を設定
app_req_bp = Blueprint('req', __name__, url_prefix='/req')

@app_req_bp.route('/', methods=['GET'])
def request_form():
    student_id = request.args.get('student')
    return render_template('club_create/request_form.html', student = student_id)

@app_req_bp.route('/request_conf', methods=['POST'])
def request_conf():
    club_name = request.form.get('club_name')
    leader_mail = request.form.get('leader_mail')
    menber_adress1  =request.form.get('member_adress1')
    menber_adress2  =request.form.get('member_adress2')
    menber_adresses = request.form.get('member_adresses')
    member_list = []
    member_list.append(leader_mail)
    if db.student_seach_from_mail(menber_adress1):
        member_list.append(menber_adress1)
    else : print("メールアドレスが登録されていません")
    if db.student_seach_from_mail(menber_adress2):
        member_list.append(menber_adress2)
    else : print('メールアドレスが登録されていません')
    print(member_list)
    if menber_adresses != None: 
        menber_adresses = menber_adresses.splitlines()
        for row in menber_adresses:
            mail = db.student_seach_from_mail_in_clubcreate(row)
            if mail != None :
                member_list.append(mail[0])
    session['member_list'] = member_list
    objective = request.form.get('objective')
    activities = request.form.get('activities')
    introduction = request.form.get('introduction')
    note = request.form.get('note', '')
    if len(member_list) >= 2:
        return render_template('club_create/request_conf.html', club_name=club_name, leader_mail=leader_mail, member_list=member_list, objective=objective, activities=activities, introduction=introduction, note=note)
    else:
        error = '登録に失敗しました。'
    return render_template('club_create/request_form.html', error=error)

#立ち上げ申請確定
@app_req_bp.route('/request_exe', methods=['POST'])
def request_exe():
    club_name = request.form.get('club_name')
    objective = request.form.get('objective')
    activities = request.form.get('activities')
    introduction = request.form.get('introduction')
    note = request.form.get('note', '')
    member_list = session.get("member_list")
    print(member_list)
    leader_id = db.get_id(member_list[0])
    print(club_name, leader_id, objective, activities, introduction, note)
    db.request_club(club_name, leader_id, objective, activities, introduction, note)
    club_id = db.get_club_id(leader_id)
    count = 0 
    for row in member_list:
        id = db.get_id(row)
        print(id)
        if count == 0 :
            flg = True
            db.first_club_member_add(id, club_id, flg)
        else : 
            flg = False
            db.first_club_member_add(id, club_id, flg)
        count += 1
    
    return render_template('club_create/request_exe.html', student=leader_id)

if __name__ == '__main__':
    app.run(debug=True)