from flask import Flask,request,redirect,render_template,url_for,send_file,flash,session
from flask_mysqldb import MySQL
from flask_session import Session
from otp import genotp
from cmail import sendmail                     #send to gmail
import random
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from tokenreset import token
import io
from io import BytesIO       #convertinf binary into bytes for that we are importing
app=Flask(__name__)
app.secret_key='*67@hjyijk'
app.config['SESSION_TYPE']='filesystem'
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='admin'
app.config['MYSQL_DB']='spm'
Session(app)        #connecting session to app.py
mysql=MySQL(app)    #connecting mysql to app.py
@app.route('/')
def index():
    return render_template('index.html')            #to open register,login page
@app.route('/registration',methods=['GET','POST'])
def register():
    if request.method=='POST':
        rollno=request.form['rollno']
        name=request.form['name']
        group=request.form['group']
        password=request.form['password']
        code=request.form['code']
        email=request.form['email']                   #email added
        #define collage code
        ccode='sdmsmkpbsc$#23'
        if ccode==code:
            cursor=mysql.connection.cursor()
            cursor.execute('select rollno from students') #for query we use cursor this for rollno
            data=cursor.fetchall()
            cursor.execute('select email from students') #this  for email
            edata=cursor.fetchall()
            #print(data) 
            if (rollno,) in data:                       #data is already exits rollno
                flash('User already exits')             #this flash msg will display
                return render_template('register.html')#and again it will show register template
            cursor.close()
            if (email,) in edata:                       #data is already exits rollno
                flash('email already exits')             #this flash msg will display
                return render_template('register.html') #and again it will show register template      
            cursor.close()
            otp=genotp()
            subject='Thanks for registering to the application'
            body=f'Use this otp to registre{otp}'
            sendmail(email,subject,body)               #added sendmail
            return render_template('otp.html',otp=otp,rollno=rollno,name=name,group=group,password=password,email=email) #to display same page
        else:
            flash('Invalid collage code')       #to display flash message
    return render_template('register.html')    #to display (render_template is use)
@app.route('/login',methods=['GET','POST'])
def login():
    if session.get('user'):
        return redirect(url_for('home'))
    if request.method=='POST':
        rollno=request.form['id']
        password=request.form['password']
        cursor=mysql.connection.cursor()
        cursor.execute('select count(*)from students where rollno=%s and password=%s',[rollno,password])
        count=cursor.fetchone()[0]
        if count==0:
            flash('Invalid roll no or password')
            return render_template('login.html')
        else:
            session['user']=rollno             #session use to restrick homepage
            return redirect(url_for('home'))    #linkhome restricked
    return render_template('login.html')
@app.route('/studenthome')
def home():
    if session.get('user'):
        return render_template('home.html')
    else:
        return redirect(url_for('login')) 
@app.route('/logout')
def logout():
    if session.get('user'):
        session.pop('user')
        return redirect(url_for('index'))   #for logout
    else:
        flash('already logged out')
        return redirect(url_for('index'))
@app.route('/otp/<otp>/<rollno>/<name>/<group>/<password>/<email>',methods=['GET','POST'])
def otp(otp,rollno,name,group,password,email):
    if request.method=='POST':
        uotp=request.form['otp']
        print(otp)
        print(uotp)
        if otp==uotp:
            cursor=mysql.connection.cursor()
            cursor.execute('insert into students values(%s,%s,%s,%s,%s)',(rollno,name,group,password,email))
            mysql.connection.commit()
            cursor.close()
            flash('detail registered')
            return redirect(url_for('login'))
        else:
            flash('Wrong otp')
            return render_template('otp.html',otp=otp,rollno=rollno,name=name,group=group,password=password,email=email) #to display same page
@app.route('/notehome')
def notehome():
    if session.get('user'):
        rollno=session.get('user')
        cursor=mysql.connection.cursor()
        cursor.execute('select * from notes where rollno=%s',[rollno])
        notes_data=cursor.fetchall()
        print(notes_data)
        cursor.close()
        return render_template('addnotetable.html',data=notes_data)#doing dynamic
    
    else:
        return redirect(url_for('login'))
@app.route('/addnotes',methods=['GET','POST'])
def addnote():
    if session.get('user'):
        if request.method=='POST':
            title=request.form['title']
            content=request.form['content']              #request handling
            cursor=mysql.connection.cursor()
            rollno=session.get('user')
            cursor.execute('insert into notes(rollno,title,content)values(%s,%s,%s)',[rollno,title,content])
            mysql.connection.commit()               #storing in database
            cursor.close()
            flash(f'{title} added successfully')
            return redirect(url_for('notehome'))
        return render_template('notes.html')
        
    else:
        return redirect(url_for('login')) # add notes
@app.route('/viewnotes/<nid>')
def viewnotes(nid):
    cursor=mysql.connection.cursor()
    cursor.execute('select title,content from notes where nid=%s',[nid])
    data=cursor.fetchone()  #single row
    return render_template('notesview.html',data=data) #viewing notesview
@app.route('/updatenotes/<nid>',methods=['GET','POST'])
def updatenotes(nid):
    if session.get('user'):
        cursor=mysql.connection.cursor()
        cursor.execute('select title,content from notes where nid=%s',[nid])
        data=cursor.fetchone()
        cursor.close()
        if request.method=='POST':
            title=request.form['title']
            content=request.form['content']
            cursor=mysql.connection.cursor()
            cursor.execute('update notes set title=%s,content=%s where nid=%s',[title,content,nid])
            mysql.connection.commit()                                             #dml means we should give commit
            cursor.close()
            flash('Notes updated successfully')
            return redirect(url_for('notehome'))
        return render_template('updatenotes.html',data=data)
    else:
        return redirect(url_for('login'))
@app.route('/deletenotes/<nid>')
def deletenotes(nid):
    cursor=mysql.connection.cursor()
    cursor.execute('delete from notes where nid=%s',[nid])
    mysql.connection.commit()
    cursor.close()
    flash('note delete successfully')
    return redirect(url_for('notehome'))
@app.route('/fileshome')
def fileshome():
    if session.get('user'):
        cursor=mysql.connection.cursor()
        rollno=session.get('user')
        cursor.execute('select fid,filename,date from files where rollno=%s',[rollno])
        data=cursor.fetchall()                  #when query is having multiple values
        return render_template('fileuploadtable.html',data=data)
    else:
        return redirect(url_for('login'))
@app.route('/filehandling',methods=['POST'])      #for submit
def filehandling():
    file=request.files['file']          #handling request.file
    filename=file.filename          #for filename
    bin_file=file.read()            #for filedata
    rollno=session.get('user')       #checking user there or not
    cursor=mysql.connection.cursor()
    cursor.execute('insert into files(rollno, filename,filedata) values(%s,%s,%s)',[rollno,filename,bin_file])
    mysql.connection.commit()
    cursor.close()
    flash(f'{filename} uploaded successfully')
    return redirect(url_for('fileshome'))
@app.route('/viewfile/<fid>')
def viewfile(fid):
    if session.get('user'):
        cursor=mysql.connection.cursor()
        cursor.execute('select filename,filedata from files where fid=%s',[fid])
        data=cursor.fetchone()
        cursor.close()
        filename=data[0]
        bin_file=data[1]
        byte_data=BytesIO(bin_file)         #convertin binary into bytes
        return send_file(byte_data,download_name=filename)
    else:
        return redirect(url_for('login'))
@app.route('/Downloadfile/<fid>')
def downloadfile(fid):
    if session.get('user'):
        cursor=mysql.connection.cursor()
        cursor.execute('select filename,filedata from files where fid=%s',[fid])
        data=cursor.fetchone()
        cursor.close()
        filename=data[0]
        bin_file=data[1]
        byte_data=BytesIO(bin_file)         #convertin binary into bytes
        return send_file(byte_data,download_name=filename,as_attachement=True)
    else:
        return redirect(url_for('login'))
@app.route('/filedelete/<fid>')
def filedelete(fid):
    cursor=mysql.connection.cursor()
    cursor.execute('delete from files where fid=%s',[fid])
    mysql.connection.commit()
    cursor.close()
    flash('file delete successfully')
    return redirect(url_for('fileshome'))
@app.route('/forgetpassword',methods=['GET','POST'])
def forgot():
    if request.method=='POST':
        rollno=request.form['id']
        cursor=mysql.connection.cursor()
        cursor.execute('select rollno from students')
        data=cursor.fetchall()
        if(rollno,) in data:
            cursor.execute('select email from students where rollno=%s',[rollno])
            data=cursor.fetchone()[0]
            cursor.close()
            subject='Reset Password for {email}'
            body=f'Reset the password using {request.host+url_for("createpassword",token=token(rollno,120))}'
            sendmail(data,subject,body)
            flash('Reset link sent to your mail')
            return redirect(url_for('login'))
        else:
            return 'Invalid user id'
    return render_template('forgot.html')
@app.route('/createpassword/<token>',methods=['GET','POST'])
def createpassword(token):
        try:
            s=Serializer(app.config['SECRET_KEY'])
            rollno=s.loads(token)['user']
            if request.method=='POST':
                npass=request.form['npassword']
                cpass=request.form['cpassword']
                if npass==cpass:
                    cursor=mysql.connection.cursor()
                    cursor.execute('update students \
set password=%s where rollno=%s',[npass,rollno])
                    mysql.connection.commit()
                    return 'Password reset Successfull'
                else:
                    return 'Password mismatch'
            return render_template('newpassword.html')
        except Exception as e:
            print(e)
            return 'Link expired try again'


    
    
    
app.run(use_reloader=True,debug=True)

