from flask import Blueprint, render_template, request, session
import hashlib, string, random, psycopg2, os, bcrypt, datetime, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

club_search_bp =  Blueprint('club_search', __name__, url_prefix='/club_search')

def get_connection():
    url = os.environ['DATABASE_URL']
    connection = psycopg2.connect(
        host = 'ec2-3-232-218-211.compute-1.amazonaws.com',
        port = 5432,
        user = 'gqaqbmtphalgvd',
        database = 'df9807ov4tu95n',
        password = 'cfd499e6588a1ebed523b87fb09090aa8fbdd70f43ac32ff2bc715a197cf3efb'
    )
    return connection

# サークル検索
# ログイン前サークル検索
@club_search_bp.route("/club_search_nolog")
def club_search_nolog():
    return render_template("club_search/club_search_nolog.html")

@club_search_bp.route("/club_search_nologres", methods=["POST"])
def club_search_nologres():
    name = request.form.get("name")
    introduction = name
    club_list = club_search(name,introduction)
    return render_template("club_search/club_search_nologres.html", club=club_list)

#学生サークル検索
@club_search_bp.route("/club_search_stu")
def club_search_stu():
    return render_template("club_search/club_search_stu.html")

@club_search_bp.route("/club_search_resstu", methods=["POST"])
def club_search_resstu():
        name = request.form.get("name")
        introduction = name
        club_list = club_search(name,introduction)
        return render_template("club_search/club_search_resstu.html", club=club_list)

#サークルリーダーサークル検索
@club_search_bp.route("/club_search_lea")
def club_search_lea():
    return render_template("club_search/club_search_lea.html")

@club_search_bp.route("/club_search_reslea", methods=["POST"])
def club_search_reslea():
        name = request.form.get("name")
        introduction = name
        club_list = club_search(name,introduction)
        return render_template("club_search/club_search_reslea.html", club=club_list)

#学生会サークル検索
@club_search_bp.route("/club_search_cou")
def club_search_cou():
    return render_template("club_search/club_search_cou.html")

@club_search_bp.route("/club_search_rescou", methods=["POST"])
def club_search_rescou():
        name = request.form.get("name")
        introduction = name
        club_list = club_search(name,introduction)
        return render_template("club_search/club_search_rescou.html", club=club_list)

#教員用サークル検索    
@club_search_bp.route("/club_search_tea")
def club_search_tea():
    return render_template("club_search/club_search_tea.html")

@club_search_bp.route("/club_search_restea", methods=["POST"])
def club_search_restea():
        name = request.form.get("name")
        introduction = name
        club_list = club_search(name,introduction)
        return render_template("club_search/club_search_restea.html", club=club_list)
    
#サークル検索機能
def club_search(name,introduction):
    try:
        connection = get_connection()
        cursor = connection.cursor()
        sql = "SELECT * FROM club WHERE name LIKE %s or introduction LIKE %s"
        name2 = "%" + name + "%"
        introduction2 = "%" + introduction + "%"
        cursor.execute(sql,(name2,introduction2))
        rows = cursor.fetchall()
    except  psycopg2.DatabaseError:
        flg = False
    finally:
        cursor.close()
        connection.close()
    return rows
