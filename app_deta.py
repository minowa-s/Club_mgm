from flask import Flask, render_template, request, Blueprint
import db

club_deta = Blueprint('app_deta', __name__, url_prefix='/app_req')

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # セッション管理のための秘密鍵を設定

@club_deta.route('/approve_list_st')
def approve_list():
    return render_template('approve_list_st.html')

@club_deta.route('/', methods=['GET'])
def approve_list_st():
    return render_template('approve_list_te.html')

@club_deta.route('/request_detail')
def get_request():
    request_name = db.get_request_club()
    return render_template('request_.html', request_detail=request_name)

@club_deta.route('/request_detail')
def get_request_exe():
    request_detail = db.get_club_dedtail()
    return render_template('request_detail.html', request_detail=request_detail)

if __name__ == '__main__':
    app.run(debug=True)