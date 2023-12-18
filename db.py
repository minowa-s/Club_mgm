import os, psycopg2

def get_connection():
    url = os.environ['DATABASE_URL']
    connection = psycopg2.connect(url)
    return connection

#サークル立ち上げ申請
def request_club(club_name, leader_mail, objective, activities, introduction, note):
    sql = 'INSERT INTO club VALUES (default, %s, %s, %s, %s, %s, %s, 0)'
    try : # 例外処理
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql, (club_name, leader_mail, objective, activities, introduction, note))
        count = cursor.rowcount # 更新件数を取得
        connection.commit()
    except psycopg2.DatabaseError: # Java でいうcatch 失敗した時の処理をここに書く
        count = 0 # 例外が発生したら0 をreturn する。
    finally: # 成功しようが、失敗しようが、close する。
        cursor.close()
        connection.close()
    return count

def get_request_club():
    connection = get_connection()
    cursor = connection.cursor()
    sql = "SELECT name, leader_id, objective, activities, introduction FROM club where name = 'Python開発サークル'"
    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return rows

#サークル詳細
def get_club_dedtail(club_id):
    connection = get_connection()
    cursor = connection.cursor()
    sql = "SELECT name, leader_id, objective, activities, introduction, note FROM club where club_id = %s"
    cursor.execute(sql, (club_id,))
    rows = cursor.fetchone()
    cursor.close()
    connection.close()
    return rows

#サークル立ち上げ申請に入っている学生idの取得
def get_student_id_from_student_club(club_id):
    connection = get_connection()
    cursor = connection.cursor()
    sql = "SELECT student_id FROM student_club where club_id = %s and is_leader = False"
    cursor.execute(sql, (club_id,))
    student_id_list = cursor.fetchall()
    cursor.close()
    connection.close()
    return student_id_list

def get_student_mail(student_id):
    connection = get_connection()
    cursor = connection.cursor()
    sql = "SELECT mail FROM student WHERE student_id = %s"
    cursor.execute(sql, (student_id,))
    student_mail = cursor.fetchone()
    cursor.close()
    connection.close()
    return student_mail
#=========================================================
#サークル申請削除
def delete_request(club_id):
    delete_from_student_club(club_id)
    sql = "DELETE FROM club WHERE club_id = %s"
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(sql, (club_id,))
    connection.commit()
    cursor.close()
    connection.close()
    
def delete_from_student_club(club_id):
    sql = "DELETE FROM student_club WHERE club_id = %s"
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(sql, (club_id,))
    connection.commit()
    cursor.close()
    connection.close()