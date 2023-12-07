from flask import Flask, render_template, request
import db

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # セッション管理のための秘密鍵を設定

@app.route('/', methods=['GET'])
def request_form():
    return render_template('request_form.html')

@app.route('/request_exe', methods=['POST'])
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
    app.run(debug=True)