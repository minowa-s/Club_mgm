import os, psycopg2

def get_connection():
    url = os.environ['DATABASE_URL']
    connection = psycopg2.connect(url)
    return connection

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

    sql = "SELECT club_name, leader_mail, objective, activities, introduction FROM club where club_name = 'Python開発サークル'"

    cursor.execute(sql)
    rows = cursor.fetchall()
        
    cursor.close()
    connection.close()
    return rows

request_detail = get_request_club()
print(request_detail)

def get_club_dedtail():
    connection = get_connection()
    cursor = connection.cursor()

    sql = "SELECT club_name, leader_mail, objective, activities, introduction, note FROM club where club_name = 'Pythonサークル'"

    cursor.execute(sql)
    rows = cursor.fetchall()
        
    cursor.close()
    connection.close()
    return rows