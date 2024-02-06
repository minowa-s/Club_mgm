from flask import Flask,Blueprint,  render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os, psycopg2, string, random, hashlib, db, club

app = Flask(__name__)
app.secret_key = 'secret_key'

#ブループリントimport-----------------
from account import account_bp       
app.register_blueprint(account_bp)
from club import club_bp
app.register_blueprint(club_bp)
from club2 import club_bp2
app.register_blueprint(club_bp2)
from app_data import app_data_bp
app.register_blueprint(app_data_bp)
from mypage import mypage_bp
app.register_blueprint(mypage_bp)
from club_search import club_search_bp
app.register_blueprint(club_search_bp)
from club_edit import club_edit_bp
app.register_blueprint(club_edit_bp)
from account_search import account_search_bp
app.register_blueprint(account_search_bp)
from account_delete import account_delete_bp
app.register_blueprint(account_delete_bp)
from teacher_mgm import teacher_mgm_bp
app.register_blueprint(teacher_mgm_bp)
from club_withdrawal import club_withdrawal_bp
app.register_blueprint(club_withdrawal_bp)
from admin import admin_bp
app.register_blueprint(admin_bp)
from app_req import app_req_bp
app.register_blueprint(app_req_bp)
from gakuseikai import gakuseikai_bp
app.register_blueprint(gakuseikai_bp)
from leader import leader_bp
app.register_blueprint(leader_bp)
#------------------------------------

#DB接続
def get_connection():
    url = os.environ['DATABASE_URL']
    connection = psycopg2.connect(url)
    return connection

@app.route('/')
def index():
    club_list = club.club_list()
    return render_template('top/top.html', club_list=club_list)

@app.route('/backtop_s', methods=['post'])
def backtop_student():
    id = request.form.get('student')
    club_list = club.club_list()
    student = db.get_student(id)
    return render_template('top/top_student.html', club_list=club_list, student=student)

@app.route('/backtop_t')
def backtop_teacher():
    club_list = club.club_list()
    return render_template('top/top_teacher.html', club_list=club_list)

@app.route('/backtop_l', methods=['post'])
def backtop_leader():
    id = request.form.get('student')
    club_list = club.club_list()
    student = db.get_student(id)
    return render_template('top/top_leader.html', club_list=club_list, student=student)

@app.route('/backtop_g')
def backtop_gakuseikai():
    club_list = club.club_list()
    return render_template('top/top_council.html', club_list=club_list)

if __name__ == '__main__':
    app.run(debug=True)