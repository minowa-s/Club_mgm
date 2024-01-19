from flask import Flask, render_template, request
from flask import Blueprint
import db

app_req_bp = Blueprint('app_req', __name__, url_prefix='/app_req')

@app_req_bp.route('/', methods=['GET'])
def request_form():
    return render_template('request_form.html')

@app_req_bp.route('/request_exe', methods=['POST'])
def request_exe():
    club_name = request.form.get('club_name')
    leader_mail = request.form.get('leader_mail')
    objective = request.form.get('objective')
    activities = request.form.get('activities')
    introduction = request.form.get('introduction')
    note = request.form.get('note', '')
    
    count = db.request_club(club_name, leader_mail, objective, activities, introduction, note)
    
    if count == 1:
        msg = '登録が完了しました。'
        return render_template('request_form.html', msg=msg)
    else:
        error = '登録に失敗しました。'
        return render_template('request_form.html', error=error)

if __name__ == '__main__':
    app_req_bp.run(debug=True)