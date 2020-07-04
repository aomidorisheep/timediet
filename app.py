import sqlite3

import random

from flask import Flask , render_template , redirect , session , request

app = Flask(__name__)

app.secret_key = "GraduateProduction"


@app.route("/")
def top():
    return render_template("01_top.html")

@app.route("/registry", methods=["GET", "POST"])
def registry():
    if request.method == "GET":
        if 'user_id' in session :
            return redirect ('/main')
        else:
            return render_template("02_registory.html")

    else:
        name = request.form.get("name")
        password = request.form.get("password")
        age = request.form.get("age")
        habit = request.form.get("habit")
        time = request.form.get("time")
        conn = sqlite3.connect('application.db')
        c = conn.cursor()
        c.execute("insert into user_info values(null,?,?,?,?,?)", (name,password,age,habit,time))
        conn.commit()
        conn.close()
        return redirect('/login')

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if 'user_id' in session :
            return redirect("/main")
        else:
            return render_template("03_login.html")
    else:
        name = request.form.get("name")
        password = request.form.get("password")
        conn = sqlite3.connect('application.db')
        c = conn.cursor()
        c.execute("select id from user_info where name = ? and password = ?", (name, password))
        user_id = c.fetchone()
        conn.close()

        if user_id is None:
            # ログイン失敗 → ログイン画面
            return render_template("03_login.html")
        else:
            session['user_id'] = user_id[0]
            return redirect("/main")

@app.route("/main")
def main():
    user_id = session['user_id']
    conn = sqlite3.connect('application.db')
    c = conn.cursor()
    #登録直後はinputへ飛ぶ
    c.execute("select total_time from total where user_id = ?", (user_id,))
    time = c.fetchone()
    if time is None:
        return redirect("/input")
    else:
        # 名前の取得
        c.execute("select name from user_info where id = ?", (user_id,))
        name = c.fetchone()

        # 習慣の取得
        c.execute("select habit from user_info where id = ?", (user_id,))
        habit = c.fetchone()
            
        # 累計時間の取得
        c.execute("select sum(total_time) from total where user_id = ?", (user_id,))
        total_time = c.fetchone()

        # 80歳までの時間計算
        c.execute("select age from user_info where id = ?", (user_id,))
        age = c.fetchone()
        c.execute("select avg(total_time) from total where user_id = ?", (user_id,))
        average_time = c.fetchone()
        untill80 = average_time[0] * 365 * (80 - age[0]) 
        day = round(untill80 / 60 / 24)
        hour = round(untill80  / 60 % 24)
        c.close()        
        return render_template("04_main.html", name = name, habit = habit, total_time = total_time, day = day, hour = hour)
    
@app.route("/input")
def input():
    user_id = session['user_id']
    conn = sqlite3.connect('application.db')
    c = conn.cursor()    
    c.execute("select name from user_info where id = ?", (user_id,))
    name = c.fetchone()
    c.execute("select habit from user_info where id = ?", (user_id,))
    habit = c.fetchone()
    c.close()
    return render_template("05_MyPage2.html", name = name, habit = habit)

@app.route("/mypage3", methods=["POST"])
def mypage3():
    # 入力された時間をデータベースに追加
    user_id = session["user_id"]    
    total_time = request.form.get("total_time")
    conn = sqlite3.connect("application.db")
    c = conn.cursor()
    c.execute("insert into total values(null,?,?)", (user_id, total_time))
    conn.commit()

    # 格言の表示
    c.execute("select proverbs from proverb")
    proverblist = []
    for row in c.fetchall():
        # rowの中身を確認
        proverblist.append({"proverb":row[0]})
    conn.close()
    proverb = random.choice(proverblist)
    proverb = proverb['proverb']
    # proverblistの中身を確認
    print(proverblist)
    print("---------------------------------")
    print(proverb)
    print("---------------------------------")
    return render_template("06_random.html", proverb = proverb)






@app.route("/logout")
def logout():
    session.pop('user_id',None)    
    return render_template("09_logout.html")




if __name__ == "__main__":
    # 開発者モードに設定中
    app.run(debug=True)