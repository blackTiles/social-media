from flask import Flask, render_template, request, redirect, session, url_for, flash
from datetime import timedelta
from datetime import datetime
import mysql.connector
import os
import random
import string
from werkzeug.utils import secure_filename
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client 

app = Flask(__name__)
app.secret_key=os.urandom(24)
app.permanent_session_lifetime = timedelta(hours=2)
db = mysql.connector.connect(host='localhost',user='root',password='', database='flaskdb')
cursor=db.cursor()
UPLOAD_FOLDER = 'static/images/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

     
@app.route("/")
def index():
    if 'user_id' in session:
        cursor.execute("""SELECT * FROM users WHERE id='{}'""".format(session['user_id']))
        user = cursor.fetchone()
        if user[8]=="1":
            cursor.execute("""SELECT * FROM posts ORDER BY postid DESC""")
            content = cursor.fetchall()
            return render_template("posts.html",usr=[user,content])
        else:
            return redirect("/verifyPage/{}".format(user[0]))
    else:
        return redirect("/form")

@app.route("/form")
def form():
    if "user_id" in session:
        return redirect(url_for("index"))
    else:
        return render_template("form.html")

@app.route("/login", methods=['POST','GET'])
def login():
    if request.method=="POST":
        l_email = request.form['lemail']
        l_pass = request.form['lpass']
        if l_email or l_pass != "":
            cursor.execute("""SELECT * FROM users WHERE email='{}' AND password='{}'""".format(l_email,l_pass))
            users = cursor.fetchall()
            if len(users)>0:                
                session["user_id"] = users[0][0]
                session.permanent = True
                return redirect(url_for("index"))
            else:
                flash("The entered email or password doesn't match")
                return redirect("/form")
        else:
            flash("Leaving blank won't log you in.......!")
            return redirect("/form")
    else:
        flash("Don't play with urls. You won't have anything...!")
        return redirect("/form")

@app.route("/signup", methods=['POST','GET'])
def signup():
    if request.method=="POST":
        f_name = request.form['fname']
        l_name = request.form['lname']
        s_email = request.form['semail']
        s_pass = request.form['spass']
        if f_name or s_email or s_pass != '':
            cursor.execute("""SELECT * FROM users WHERE email='{}'""".format(s_email))
            verify = cursor.fetchall()
            if len(verify)==0:
                otp = str(''.join(random.choice(string.digits) for i in range(6)))
                cursor.execute("""INSERT INTO users(firstname, lastname, email, password, last_otp) VALUES('{}','{}','{}','{}','{}')""".format(f_name,l_name,s_email,s_pass,otp))
                db.commit()
                cursor.execute("""SELECT * FROM users WHERE email='{}' AND password='{}'""".format(s_email,s_pass))
                s_rows = cursor.fetchall()
                session["user_id"] = s_rows[0][0]
                session.permanent=True
                #send otp
                sender_email = "black4tiles@gmail.com"
                receiver_email = s_email
                password = "piastrellenere?mean4805"
                message = MIMEMultipart("alternative")
                message["Subject"] = "OTP verification"
                message["From"] = sender_email
                message["To"] = receiver_email
                html = """\
                        <html>
                        <head>
                        <meta charset="UTF-8">
                        <meta http-equiv="X-UA-Compatible" content="IE=edge">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        </head>
                        <body>
                            <div style="align-items:center;">
                                <div style="margin:0px auto;text-align:center;"><img src="https://scontent.fpat2-1.fna.fbcdn.net/v/t1.0-0/p526x296/149769738_232347528522986_2842490704685962839_o.jpg?_nc_cat=104&ccb=3&_nc_sid=730e14&_nc_ohc=ehEWDBits3AAX-u6VhH&_nc_ht=scontent.fpat2-1.fna&tp=6&oh=fc8c17661e83077ade1ac030f14e973b&oe=604D9EC8" width="100" height="100" /></div>
                                <br />
                                <h1 style="font-family:sans-serif; color:grey;text-align:center;">Email Confirmation OTP</h1>
                                <br />
                                <h1 style="font-family:sans-serif; padding:10px; border: 2px dashed black;text-align:center;">{}</h1>
                                <br />
                                <p style="text-align:center">Thank you for being a member of black tiles</p>
                                <hr />
                            </div>
                        </body>
                        </html>
                        """.format(otp)
                part1 = MIMEText(html, "html")
                message.attach(part1)
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                    server.login(sender_email, password)
                    server.sendmail(sender_email, receiver_email, message.as_string())
                return redirect("/verifyPage/{}".format(session["user_id"]))
            else:
                flash("This email has already been used....")
                return redirect("/form")
        else:
            flash("Leaving blank won't log you in.......!")
            return redirect("/form")
    else:
        flash("Don't play with urls. You won't have anything...!")
        return redirect("/form")

@app.route("/verifyPage/<id>")
def verifyPage(id):
    if "user_id" in session:
        cursor.execute("SELECT * FROM users WHERE id='{}'".format(session["user_id"]))
        user = cursor.fetchone()
        if user[8] != "1":
            return render_template("verifyaccount.html", user=user)
        else:
            return redirect(url_for("index"))
    else:
        return redirect("/form")
        

@app.route("/deleteAccount/<account_id>")
def deleteAccount(account_id):
    if "user_id" in session:
        cursor.execute("SELECT * FROM users WHERE id='{}'".format(session["user_id"]))
        user = cursor.fetchone()
        if user[8] != "1":
            cursor.execute("DELETE FROM users WHERE id='{}'".format(session["user_id"]))
            db.commit()
            session.pop("user_id", None)
            session.permanent = False
            return redirect(url_for("index"))
        else:
            return redirect(url_for("index"))
    else:
        return redirect("/form")

@app.route("/confirmOTP/<accountID>", methods=["POST","GET"])
def confirmOTP(accountID):
    if request.method=="POST":
        get_otp = request.form["otp"]
        if get_otp != "":
            cursor.execute("SELECT * FROM users WHERE id='{}'".format(session["user_id"]))
            mailed_otp = cursor.fetchone()
            if get_otp == mailed_otp[7]:
                cursor.execute("""UPDATE users SET is_verified='{}' WHERE id='{}'""".format('1',session['user_id']))
                db.commit()
                return redirect(url_for("index"))
            else:
                return redirect("/verifyPage/{}".format(accountID))
        else:
            return redirect("/verifyPage/{}".format(accountID))
    else:
        return redirect(url_for("index"))

@app.route("/upload",methods=["POST","GET"])
def upload():
    if 'user_id' in session:
        if request.method == "POST":
            content = request.form['postcontent']
            img = request.files['postimage']
            if img != "":
                name = img.filename
                filename = secure_filename(img.filename)
                img.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                letters = string.ascii_lowercase + string.ascii_uppercase + string.ascii_letters + string.digits
                cursor.execute("SELECT * FROM users WHERE id='{}'".format(session['user_id']))
                first_name = cursor.fetchone()
                newname = first_name[3]+first_name[4]+''.join(random.choice(letters) for i in range(24))
                image_rename = os.rename(f'static/images/uploads/{name}', f"static/images/uploads/{newname}.jpg")
                image_file = f'{newname}.jpg'
                current_time = datetime.now()
                get_current_time = current_time.strftime("%d %b, %I:%M %p")
                cursor.execute("""INSERT INTO posts(userid,content,image_name,firstname,lastname,profile_image,upload_time) VALUES("{}","{}","{}","{}","{}","{}","{}")""".format(session['user_id'],content,image_file,first_name[3],first_name[4],first_name[5],get_current_time))
                db.commit()
                flash("Image uploaded successfully")
                return redirect(url_for("index"))
            else:
                flash("Image field shouldn't be blank")
                return redirect(url_for("index"))
        else:
            return redirect(url_for("index"))
    else:
        return redirect("/form")

@app.route("/logout", methods=['POST','GET'])
def logout():
    session.pop("user_id", None)
    session.permanent = False
    return redirect("/form")

@app.route("/profile/<id>")
def profile(id):
    if 'user_id' in session:
        cursor.execute("""SELECT * FROM users WHERE id='{}'""".format(session['user_id']))
        user = cursor.fetchone()
        cursor.execute("""SELECT * FROM posts WHERE userid='{}'""".format(session['user_id']))
        content = cursor.fetchall()
        return render_template("profilesession.html",usr=[user,content])
    else:
        return redirect("/form")

@app.route("/profile/editprofile/<id>")
def editprofile(id):
    if 'user_id' in session:
        cursor.execute("""SELECT * FROM users WHERE id='{}'""".format(session['user_id']))
        user = cursor.fetchone()
        return render_template("editprofile.html",usr=[user])
    else:
        return redirect("/form")


@app.route("/delete_post/<postid>")
def delete_post(postid):
    if 'user_id' in session:
        cursor.execute("SELECT * FROM posts WHERE postid='{}'".format(postid))
        image_name = cursor.fetchone()
        os.remove(f'static/images/uploads/{image_name[3]}')
        cursor.execute("""DELETE FROM comments WHERE postid='{}' """.format(postid))
        db.commit()
        cursor.execute("DELETE FROM posts WHERE postid='{}'".format(postid))
        db.commit()
        cursor.execute("""SELECT * FROM users WHERE id='{}'""".format(session['user_id']))
        user = cursor.fetchone()
        return redirect(f"/profile/{user[0]}")
    else:
        return redirect("/form")

@app.route("/uploadprofile",methods=["POST","GET"])
def uploadprofile():
    if 'user_id' in session:
        if request.method == "POST":
            img = request.files['profileimage']
            if img != "":
                name = img.filename
                filename = secure_filename(img.filename)
                img.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                letters = string.ascii_lowercase + string.ascii_uppercase + string.ascii_letters + string.digits
                cursor.execute("SELECT * FROM users WHERE id='{}'".format(session['user_id']))
                first_name = cursor.fetchone()
                newname = first_name[3]+first_name[4]+''.join(random.choice(letters) for i in range(24))
                image_rename = os.rename(f'static/images/uploads/{name}', f"static/images/uploads/{newname}.jpg")
                image_file = f'{newname}.jpg'
                cursor.execute("""UPDATE users SET profileimage="{}" WHERE id="{}" """.format(image_file, session['user_id']))
                db.commit()
                cursor.execute("""UPDATE posts SET profile_image="{}" WHERE userid="{}" """.format(image_file, session['user_id']))
                db.commit()
                cursor.execute("""UPDATE comments SET profile_image="{}" WHERE userid="{}" """.format(image_file, session['user_id']))
                db.commit()
                return redirect("/profile/editprofile/{}".format(session['user_id']))
            else:
                return redirect("/profile/editprofile/{}".format(session['user_id']))
        else:
            return redirect(url_for("index"))
    else:
        return redirect("/form")

@app.route("/saveProfileEdited",methods=["POST","GET"])
def saveProfileEdited():
    if "user_id" in session:
        if request.method=="POST":
            f_name = request.form['firstname']
            l_name = request.form['lastname']
            bio_data = request.form['biodata']
            if f_name or l_name or bio_data != "":
                cursor.execute("""UPDATE users SET firstname="{}", lastname="{}", biodata="{}" WHERE id="{}" """.format(f_name, l_name, bio_data, session['user_id']))
                db.commit()
                cursor.execute("""UPDATE posts SET firstname="{}", lastname="{}" WHERE userid="{}" """.format(f_name, l_name, session['user_id']))
                db.commit()
                cursor.execute("""UPDATE comments SET firstname="{}", lastname="{}" WHERE userid="{}" """.format(f_name, l_name, session['user_id']))
                db.commit()
                return redirect("/profile/editprofile/{}".format(session['user_id']))
            else:
                return redirect("/profile/editprofile/{}".format(session['user_id']))
        else:
            return redirect(url_for("index"))
    else:
        return redirect("/form")

@app.route("/comments/<userid_>/<postid_>")
def comment(userid_, postid_):
    if "user_id" in session:
        cursor.execute("SELECT * FROM posts WHERE postid='{}'".format(postid_))
        post_row = cursor.fetchone()
        cursor.execute("SELECT * FROM comments WHERE postid='{}' ORDER BY comment_id DESC".format(postid_))
        comments_row = cursor.fetchall()
        return render_template("comments.html", post_row=post_row, comments_row=comments_row)
    else:
        return redirect("/form")

@app.route("/commentup/<_postid>",methods=["POST","GET"])
def upload_comment(_postid):
    if "user_id" in session:
        if request.method=="POST":
            com = request.form["comment"]
            cursor.execute("SELECT * FROM users WHERE id='{}'".format(session['user_id']))
            user_data = cursor.fetchone()
            current_time = datetime.now()
            get_current_time = current_time.strftime("%d %b, %I:%M %p")
            cursor.execute("""INSERT INTO comments(postid,userid,firstname,lastname,profile_image,upload_date,comment_para) VALUES("{}","{}","{}","{}","{}","{}","{}")""".format(_postid,user_data[0],user_data[3],user_data[4],user_data[5],get_current_time,com))
            db.commit()
            cursor.execute("SELECT * FROM comments WHERE postid='{}'".format(_postid))
            current_comments = cursor.fetchall()
            cursor.execute("UPDATE posts SET no_of_comments='{}' WHERE postid='{}'".format(len(current_comments),_postid))
            db.commit()
            return redirect("/comments/{}/{}".format(user_data[0],_postid))
        else:
            return redirect("/comments/{}/{}".format(user_data[0],_postid))
    else:
        return redirect("/form")

@app.route("/delete_comment/<com_id>/<pos_id>")
def delete_comment(com_id,pos_id):
    if "user_id" in session:
        cursor.execute("""DELETE FROM comments WHERE comment_id='{}' AND postid='{}' """.format(com_id,pos_id))
        db.commit()
        cursor.execute("SELECT * FROM comments WHERE postid='{}'".format(pos_id))
        current_comments = cursor.fetchall()
        cursor.execute("UPDATE posts SET no_of_comments='{}' WHERE postid='{}'".format(len(current_comments),pos_id))
        db.commit()
        return redirect("/comments/{}/{}".format(session['user_id'],pos_id))
    else:
        return redirect("/form")


@app.route("/userprofile/<user_i_d>")
def userprofile(user_i_d):
    if 'user_id' in session:
        cursor.execute("""SELECT * FROM users WHERE id='{}'""".format(user_i_d))
        user = cursor.fetchone()
        cursor.execute("""SELECT * FROM posts WHERE userid='{}'""".format(user_i_d))
        content = cursor.fetchall()
        return render_template("postprofile.html",usr=[user,content])
    else:
        return redirect("/form")

@app.route("/feedback", methods=["POST","GET"])
def feedback():
    if request.method == "POST":
        sender_name = request.form['fullname']
        sender_email = request.form['email']
        sender_msg = request.form['message']
        account_sid = 'AC9401df5424014de632b86f74d6b071e5' 
        auth_token = '02cc8f0d1a3552b731ed4196a0e3a40e' 
        client = Client(account_sid, auth_token) 
        message = client.messages.create( 
                                    from_='+15167084010',  
                                    body=f'{sender_name}\n{sender_email}\n{sender_msg}',      
                                    to='+919065568504' 
                                ) 
        return redirect("/form")
    else:
        return redirect("/form")

if __name__=="__main__":
    app.run(debug=True)