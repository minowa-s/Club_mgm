from flask import Blueprint, Flask, render_template, request
import db, club

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # セッション管理のための秘密鍵を設定
app_req_bp = Blueprint('req', __name__, url_prefix='/req')

@app_req_bp.route('/', methods=['GET'])
def request_form():
    return render_template('request_form.html')

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
    else : print("メールアドレスが登録されてないです")
    if db.student_seach_from_mail(menber_adress2):
        member_list.append(menber_adress2)
    else : print('メールアドレスが登録されてないです')
    if menber_adresses != None: 
        menber_adresses = menber_adresses.splitlines()
        print(menber_adresses)
        for row in menber_adresses:
            print(row)
            mail = db.student_seach_from_mail_in_clubcreate(row)
            if mail != None :
                member_list.append(mail[0])
    objective = request.form.get('objective')
    activities = request.form.get('activities')
    introduction = request.form.get('introduction')
    note = request.form.get('note', '')
    print(member_list)
    if len(member_list) >= 2:
        return render_template('request_conf.html', club_name=club_name, leader_mail=leader_mail, member_list=member_list, objective=objective, activities=activities, introduction=introduction, note=note)
    else:
        error = '登録に失敗しました。'
    return render_template('request_form.html', error=error)

#立ち上げ申請確定
@app_req_bp.route('/request_exe', methods=['POST'])
def request_exe():
    club_name = request.form.get('club_name')
    leader_mail = request.form.get('leader_mail')
    menber_adress1  =request.form.get('member_adress1')
    menber_adress2  =request.form.get('member_adress2')
    menber_adresses = request.form.get('menber_adresses')
    objective = request.form.get('objective')
    activities = request.form.get('activities')
    introduction = request.form.get('introduction')
    note = request.form.get('note', '')
    leader_id = db.get_id(leader_mail)
    
    db.request_club(club_name, leader_id, objective, activities, introduction, note)
    
    return render_template('request_exe.html')

if __name__ == '__main__':
    app.run(debug=True)