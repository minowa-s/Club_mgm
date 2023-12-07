from flask import Flask, render_template, request, redirect, url_for, session
import db, string, random
from datetime import timedelta

app = Flask(__name__)
app.secret_key = ''.join(random.choices(string.ascii_letters, k=256))

@app.route('/', methods=['GET'])
def approve_list_st():
    return render_template('approve_list_te.html')

@app.route('/request_detail')
def get_request_exe():
    request_detail = db.get_club_dedtail()
    return render_template('request_detail.html', request_detail=request_detail)

if __name__ == '__main__':
    app.run(debug=True)