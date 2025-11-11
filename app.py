from flask import Flask, render_template, request, redirect, url_for, session, send_file, Response
from database import (db_init, registered_user, insert_userotp, check_userotp, insert_users, 
                        check_userpassword, add_notes, display_notes, get_note, update_note_db, 
                        delete_note_db, add_file_db, get_files_db, get_file_db, delete_file_db, 
                        search_notes, password_reset_db)
import random
import smtplib
from email.message import EmailMessage
import os
from itsdangerous import URLSafeTimedSerializer

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = 'application'
serializer = URLSafeTimedSerializer(app.secret_key)

db_init()

# Load Mail Credentials from .env
admin_email = os.getenv('MAIL_USERNAME')
admin_password = os.getenv('MAIL_PASSWORD')

def send_mail(to_email, body):
    msg = EmailMessage()
    msg.set_content(body)
    msg['To'] = to_email
    msg['From'] = admin_email
    msg['Subject'] = 'OTP Verification'

    with smtplib.SMTP_SSL(os.getenv('MAIL_SERVER'), int(os.getenv('MAIL_PORT'))) as smtp:
        smtp.login(admin_email, admin_password)
        smtp.send_message(msg)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods = ['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if registered_user(email):
            return redirect(url_for('login'))

        if check_userotp(email):
            return redirect(url_for('verify_otp', email = email))

        otp = random.randint(100000, 999999)
        body = f'''Please, Enter this OTP for verification
            Do not share this OTP with anyone.
            Your OTP is {otp}'''
        send_mail(email,body)
        
        insert_userotp(username, email, password, otp)

        # return redirect(url_for('verify_otp', email = email))
        return render_template('verify_otp.html', email = email)

    return render_template('register.html')

@app.route('/verify_otp/<email>', methods = ['POST', 'GET'])
def verify_otp(email):
    if request.method == 'POST':
        otp = int(request.form.get('otp'))
        user_dict = check_userotp(email)
        db_otp = user_dict['OTP']

        if otp != db_otp:
            msg = "Invalid OTP"
            msg_type = "error"
            return render_template('verify_otp.html', message = msg, message_type = msg_type, email = email)

        else:
            user_details = check_userotp(email)
            username = user_details['USERNAME']
            password = user_details['USERPASSWORD']
            insert_users(username, email, password)
            msg = "Registered Successfully"
            msg_type = "success"

            # return redirect(url_for('login'))
            return render_template('login.html')

    return render_template('verify_otp.html', email = email)


@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form.get('usermail')
        password = request.form.get('password')
        user = check_userpassword(email, password)
        
        if user:
            username = user['USERNAME']
            userid = user['USERID']
            session['username'] = username
            session['user_id'] = userid
            return render_template('dashboard.html')

        else:
            msg = "Invalid Credentials"
            msg_type = "error"
            return render_template('login.html', message = msg, message_type = msg_type)

    return render_template('login.html')

@app.route('/forgot_password', methods = ['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        if not registered_user(email):
            msg = 'No User Registered'
            msg_type = 'error'
            return render_template('register.html', message = msg, message_type = msg_type)

        token = serializer.dumps(email, salt = 'password-reset')
        reset_url = url_for('reset_password', token = token, _external = True)
        body = f"Follow this link for resetting your password: {reset_url}"
        send_mail(email, body)
    return render_template('forgot_password.html')

@app.route('/reset_password/<token>', methods = ['POST', 'GET'])
def reset_password(token):
    email = serializer.loads(token, salt = 'password-reset')
    if request.method == 'POST':
        password = request.form.get('password')
        password_reset_db(email, password)
        msg = 'Password Reset Successful'
        msg_type = 'success'
        return render_template('login.html', message = msg, message_type = msg_type)
    return render_template('reset_password.html', token = token)

@app.route('/dashboard')
def dashboard():
    if session:
        return render_template('dashboard.html')
    msg = 'No User Logged In'
    msg_type = 'error'
    return render_template('login.html', message = msg, message_type = msg_type)

@app.route('/add_note', methods = ['POST', 'GET'])
def add_note():
    if not session:
        msg = 'No User Logged In'
        msg_type = 'error'
        return render_template('login.html', message = msg, message_type = msg_type)
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        userid = session['user_id']
        add_notes(userid, title, content)
        msg = 'Notes Added Successfully'
        msg_type = 'success'
        return render_template('add_note.html', message = msg, message_type = msg_type)

    return render_template('add_note.html')

@app.route('/view_notes')
def view_notes():
    if not session:
        msg = 'No User Logged In'
        msg_type = 'error'
        return render_template('login.html', message = msg, message_type = msg_type)
    
    userid = session['user_id']
    notes = display_notes(userid)
    
    return render_template('view_notes.html', notes = notes)

@app.route('/view_note/<int:nid>')
def view_note(nid):
    if not session:
        msg = 'No User Logged In'
        msg_type = 'error'
        return render_template('login.html', message = msg, message_type = msg_type)
    
    note = get_note(nid)
    return render_template('view_note.html', note = note)

@app.route('/update_note/<int:nid>', methods=['POST', 'GET'])
def update_note(nid):
    if not session:
        msg = 'No User Logged In'
        msg_type = 'error'
        return render_template('login.html', message=msg, message_type=msg_type)

    note = get_note(nid)

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        update_note_db(nid, content, title)
        return redirect(url_for('view_notes'))

    return render_template('update_note.html', note = note)

@app.route('/delete_note/<int:nid>')
def delete_note(nid):
    if not session:
        msg = 'No User Logged In'
        msg_type = 'error'
        return render_template('login.html', message=msg, message_type=msg_type)

    delete_note_db(nid)
    return redirect(url_for('view_notes'))

@app.route('/upload_file', methods = ['POST', 'GET'])
def upload_file():
    if not session:
        msg = 'No User Logged In'
        msg_type = 'error'
        return render_template('login.html', message=msg, message_type=msg_type)

    if request.method == 'POST':
        file = request.files.get('file')
        filename = file.filename
        filepath = os.path.join('uploads', filename)
        file.save(filepath)
        userid = session['user_id']
        add_file_db(filename, filepath, userid)
        msg = 'File Uploaded Successfully'
        msg_type = 'success'
        
        return render_template('upload_file.html', message = msg, message_type = msg_type)
    
    return render_template('upload_file.html')

@app.route('/view_files')
def view_files():
    if not session:
        message='No user logged in'
        message_type='error'
        return render_template('login.html', message=message, message_type=message_type)
    
    userid = session['user_id']
    files = get_files_db(userid)
    return render_template('view_files.html', files=files)

@app.route('/view_file/<int:fid>')
def view_file(fid):
    if not session:
        message='No user logged in'
        message_type='error'
        return render_template('login.html', message=message, message_type=message_type)
    
    file = get_file_db(fid)
    file_path = file['FILEPATH']
    return send_file(file_path, as_attachment = False)

@app.route('/download_file/<int:fid>')
def download_file(fid):
    if not session:
        message='No user logged in'
        message_type='error'
        return render_template('login.html', message=message, message_type=message_type)
    
    file = get_file_db(fid)
    file_path = file['FILEPATH']
    return send_file(file_path, as_attachment = True)

@app.route('/delete_file/<int:fid>')
def delete_file(fid):
    if not session:
        message='No user logged in'
        message_type='error'
        return render_template('login.html', message=message, message_type=message_type)
    
    file = get_file_db(fid)
    file = get_file_db(fid)
    file_path = file['FILEPATH']
    os.remove(file_path)
    delete_file_db(fid)
    return redirect(url_for('view_files'))

@app.route('/search', methods=['GET', 'POST'])
def search():
    if not session:
        message='No user logged in'
        message_type='error'
        return render_template('login.html', message=message, message_type=message_type)
    
    if request.method == 'POST':
        query = request.form.get('query')
        userid = session['user_id']
        results = search_notes(userid, query)
        
        if results:
            msg = f"Found {len(results)} matching"
            msg_type = "success"
        else:
            msg = "No notes found for your search"
            msg_type = "error"
        
        return render_template('search.html', notes=results, message=msg, message_type=msg_type)
    
    return render_template('search.html', notes=None)

@app.route('/export_notes')
def export_notes():
    userid = session['user_id']
    user_notes = display_notes(userid)
    text = ''
    for note in user_notes:
        text += note['TITLE'] + '\n'
        text += note['CONTENT'] + '\n'
        text += '\n'
    
    return Response(text, mimetype = 'text/plain', headers = {'Content-Disposition' : 'attachable'})

@app.route('/logout')
def logout():
    if session:
        session.pop('username')
        session.pop('user_id')
        msg = 'Logged Out Successfully'
        msg_type = 'success'
        return render_template('login.html', message = msg, message_type = msg_type)
    msg = 'No User Logged In'
    msg_type = 'error'
    return render_template('login.html', message = msg, message_type = msg_type)

if __name__ == '__main__':
    app.run(debug=True)