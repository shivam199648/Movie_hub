
from logging import exception
from flask import Flask, render_template, request, redirect, url_for, session,json,flash
import re
import sqlite3#mysql.connector
from datetime import datetime as dt


app = Flask(__name__)
database=sqlite3.connect('movie_finder.db')#mysql.connector.connect(host='localhost',user='root',passwd='12345',database='movie_finder')
cursor=database.cursor()#(buffered=True)
app.secret_key = 'my_secret'

@app.route("/")
def main():
    try:
      return render_template('signin.html')
    except Exception as e:
        raise e


@app.route('/showSignUp')
def showSignUp():
    try:
       return render_template('signup.html')
    except Exception as e:
        raise e

@app.route('/signIn')
def showSignIn():
    try:
       return render_template('signin.html')
    except Exception as e:
        raise e

@app.route('/signIn_user',methods=['GET','POST'])
def login():
    try:
      msg = ''
      # Check if "username" and "password" POST requests exist (user submitted form)
      if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['email']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor.execute(f"create table if not exists user (user_id bigint auto_increment,email_id varchar(50),user_name varchar(40),user_type varchar(30) ,password varchar(30),city varchar(30),state varchar(30), Primary key (user_id))")
        database.commit()
        cursor.execute(f"SELECT user_id,user_name,email_id,user_type FROM user WHERE email_id = '{username}' AND password = '{password}'")
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[1]
            session['user_type']=account[2]
            # Redirect to home page
            
            return redirect('/home')
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect email/password! Please Register '
            return render_template('signup.html', msg=msg)
    # Show the login form with message (if any)
    except Exception as e:
        raise e

    
@app.route('/Add_movies')
def addmovies():
    try:

        if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        
          cursor.execute(f"SELECT * FROM user WHERE user_id = {session['id']}")
          account = cursor.fetchone()
          return render_template('theater_login.html',account=account)

    except Exception as e:
        raise e

@app.route('/movies',methods=['GET','POST'])
def n_movies():
    try:
    
      movie_name=request.form['movie_name']
      theater_name=request.form['theater_name']
      seats=request.form['seats']
    
      timings=request.form['timings'].split(',')
      genre=request.form['genre']
      duration=request.form['duration']
      cost=request.form['cost']
    
      cursor.execute('CREATE TABLE IF NOT EXISTS movies(movie_id BIGINT AUTO_INCREMENT,theater_id bigint,movie_name varchar(30),theater_name varchar(30),seats bigint,booked_seats varchar(200),timings varchar(45),genre varchar(20),duration bigint,cost bigint,active_ind varchar(1), PRIMARY KEY(movie_id))')
      database.commit()
      cursor.execute(f"update movies set active_ind='0' where theater_id={session['id']}")
      for values in timings:
        cursor.execute(f'''Insert into movies(theater_id,movie_name,theater_name,seats,booked_seats,timings,genre,duration,cost,active_ind) values 
         ({session['id']},'{movie_name}','{theater_name}',{seats},'0','{values}','{genre}','{duration}',{cost},'1')''')
      database.commit()
      cursor.execute(f"select theater_id,theater_name,movie_name,sum(booked_seats) as total_seats,cost from movies where theater_id='{session['id']}' and active_ind='1' group by theater_id,theater_name,cost")
      result=cursor.fetchone()
      movie_name=result[2]
      cursor.execute(f"Create table if not exists bookings(booking_id BIGINT AUTO_INCREMENT,user_id BIGINT,theater_id bigint,movie_id bigint,seats_booked bigint,total_cost bigint,movie_schedule datetime,booking_time datetime default CURRENT_TIMESTAMP,PRIMARY KEY(booking_id))")
      database.commit()
      cursor.execute(f"select sum(total_cost),sum(seats_booked) from bookings where movie_id in (select movie_id from movies where theater_id={session['id']} and movie_name='{movie_name}')")
    
      total_cost=0
      total_ticket=0
    
      if cursor.rowcount>0:
          result_set=cursor.fetchone()
          total_cost=result_set[0]
          total_ticket=result_set[1]
        
          if total_cost is None:
              total_cost=0
      return render_template('theater_dashboard.html',result=result,total_cost=total_cost,total_ticket=total_ticket)
    except Exception as e:
        raise e

@app.route('/signUp',methods=['GET','POST'])
def register():
    try:
    # Output message if something goes wrong...
      msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
      if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
          # Create variables for easy access
          username = request.form['username']
          password = request.form['password']
          email = request.form['email']
          user_type=request.form['user_type']
          city=request.form['city']
          state=request.form['state']
      elif request.method == 'POST':
          # Form is empty... (no POST data)
          msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    
      email = request.form['email']
      cursor.execute(f"SELECT * FROM user WHERE email_id = '{email}'")
      account = cursor.fetchone()
        # If account exists show error and validation checks
      if account:
              msg = 'Account already exists!'
      elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
              msg = 'Invalid email address!'
      elif not re.match(r'[A-Za-z0-9]+', username):
              msg = 'Username must contain only characters and numbers!'
      elif not username or not password or not email:
              msg = 'Please fill out the form!'
      else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
              cursor.execute(f"create table if not exists user (user_id bigint auto_increment,email_id varchar(50),user_name varchar(40),user_type varchar(30) ,password varchar(30),city varchar(30),state varchar(30), Primary key (user_id))")
              cursor.execute(f''' insert into user(user_name,email_id,password,user_type,city,state)values( '{username}','{email}','{password}','{user_type}','{city}','{state}');''')
              database.commit()
              msg = 'You have successfully registered! Please login Now'

      return render_template('signup.html', msg=msg)
    except Exception as e:
        raise e

@app.route('/home')
def home():
    try:
    # Check if user is loggedin
      if 'loggedin' in session:
          user_id=session['id']
          print(session)
          cursor.execute(f"SELECT * FROM user WHERE user_id = {user_id}")
          account = cursor.fetchone()
        # Show the profile page with account info
          user_type=account[3]
          if user_type=='Theater':
              
              return render_template('theater_login.html',account=account)
          # User is loggedin show them the home page
          else:
             cursor.execute('CREATE TABLE IF NOT EXISTS movies(movie_id BIGINT AUTO_INCREMENT,theater_id bigint,movie_name varchar(30),theater_name varchar(30),seats bigint,booked_seats varchar(200),timings varchar(45),genre varchar(20),duration bigint,cost bigint,active_ind varchar(1), PRIMARY KEY(movie_id))')
             database.commit()
             cursor.execute(f'''select * from (select cast(movie_id as char) as movie_id,movie_name,timings,cast(concat(current_date,' ',timings) as datetime) as sp ,theater_name
             from  movies where active_ind='1' and theater_id in (select user_id from user where city in 
              (select city from user where user_id={user_id}) and user_type='Theater'))s''')
             movie_list=cursor.fetchall()
             movies='' 
             movie_id=''
             timing=''
             theater=''
             count=0
             for movie in movie_list:
                 if count==0:
                     movies=movie[1]
                     movie_id=movie[0]
                     timing=str(movie[2])
                     theater=movie[4]
                     count=1
                 else:
                     movies=movies+','+movie[1]
                     movie_id=movie_id+','+movie[0]
                     timing=timing+','+str(movie[2])
                     theater=theater+','+movie[4]
             return render_template('home.html', username=session['username'],id=session['id'],movies=movies,movie_id=movie_id,timing=timing,theater=theater)
    # User is not loggedin redirect to login page
      return redirect('/signIn')
    except Exception as e:
        raise(e)


@app.route('/profile')
def profile():
    try:

      if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        
          cursor.execute(f"SELECT * FROM user WHERE user_id = {session['id']}")
          account = cursor.fetchone()
        # Show the profile page with account info
       
          return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
      return redirect('/signIn')
    except Exception as e:
        raise e

@app.route('/logout')
def logout():
    try:
    # Remove session data, this will log the user out
      session.pop('loggedin', None)
      session.pop('id', None)
      session.pop('username', None)
   # Redirect to login page
      return redirect('/signIn')
    except Exception as e:
        raise(e)

@app.route('/theater_dashboard')
def t_dashboard():
    try:
      movie_name=''
      result=[]
      cursor.execute(f"select theater_id,theater_name,movie_name,sum(booked_seats) as total_seats,cost from movies where theater_id='{session['id']}' and active_ind='1' group by theater_id,theater_name,cost")
      if cursor.rowcount>0:
        result=cursor.fetchone()
    
        movie_name=result[2]
      cursor.execute(f"select sum(total_cost),sum(seats_booked) from bookings where movie_id in (select movie_id from movies where theater_id={session['id']} and movie_name='{movie_name}')")
    
      total_cost=0
      total_ticket=0
    
      if cursor.rowcount>0:
          result_set=cursor.fetchone()
          total_cost=result_set[0]
          total_ticket=result_set[1]
        
          if total_cost is None:
              total_cost=0
      return render_template('theater_dashboard.html',result=result,total_cost=total_cost,total_ticket=total_ticket)
    except Exception as e:
        raise(e)
        

    


@app.route('/Find_Shows',methods=['GET','POST'])
def find_shows():
    try:

      Theater=request.form.get("Theater")
      Movie=request.form.get("Movies")
      Timings=request.form.get("timings")
      Date=request.form.get("Dates")
      booking_datetime=str(Date)+" "+str(Timings)
      print(request.form)
      cursor.execute(f"select theater_id,theater_name,movie_id,movie_name,booked_seats,seats,genre,cost,duration from movies where movie_name='{Movie}' and theater_name='{Theater}' and timings='{Timings}' and active_ind='1'")
      movie_info=cursor.fetchone()
      print(booking_datetime)
      cursor.execute(f"Create table if not exists bookings(booking_id BIGINT AUTO_INCREMENT,user_id BIGINT,theater_id bigint,movie_id bigint,seats_booked bigint,total_cost bigint,movie_schedule datetime,booking_time datetime default CURRENT_TIMESTAMP,PRIMARY KEY(booking_id))")
      cursor.execute(f"select sum(seats_booked) from bookings where movie_id={movie_info[2]} and movie_schedule='{booking_datetime}'")
      database.commit()
      booked_seats=0
    
      if cursor.rowcount>0:
          booked_seats=cursor.fetchone()[0]
          if booked_seats is None:
              booked_seats=0
    
      seats_left=int(movie_info[5])-int(booked_seats)
      return render_template('booking_page.html',movie_info=movie_info,seats_left=seats_left,booking_datetime=booking_datetime)
    except Exception as e:
        raise e
    

@app.route('/user_dashboard',methods=['GET','POST'])
def user_dashboard():
    try:
      if 'theater_name' in request.form:
         theater_name=request.form.get('theater_name')
         movie_name=request.form.get('movie_name')
         selected_seats=request.form.get('select_seats')
         total_cost=request.form.get('total_cost')
         timings=request.form.get('timings')
         time=timings.split(" ")[1]
         user_id=session['id']
         cursor.execute(f"select movie_id,theater_id from movies where movie_name='{movie_name}' and theater_name='{theater_name}' and timings='{time}' and active_ind='1'")
         movie_theater=cursor.fetchone()
         movie_id=movie_theater[0]
         theater_id=movie_theater[1]
         cursor.execute(f"Create table if not exists bookings(booking_id BIGINT AUTO_INCREMENT,user_id BIGINT,theater_id bigint,movie_id bigint,seats_booked bigint,total_cost bigint,movie_schedule datetime,booking_time datetime default CURRENT_TIMESTAMP,PRIMARY KEY(booking_id))")

         cursor.execute(f"Insert into bookings(user_id,theater_id,movie_id,seats_booked,total_cost,movie_schedule) values ({user_id},{theater_id},{movie_id},{selected_seats},{total_cost},'{timings}')")
      
      cursor.execute(f"Create table if not exists bookings(booking_id BIGINT AUTO_INCREMENT,user_id BIGINT,theater_id bigint,movie_id bigint,seats_booked bigint,total_cost bigint,movie_schedule datetime,booking_time datetime default CURRENT_TIMESTAMP,PRIMARY KEY(booking_id))")
      database.commit()
      cursor.execute(f"select distinct booking_id,movie_name,theater_name,movie_schedule,seats_booked,total_cost from bookings inner join movies on bookings.movie_id=movies.movie_id where user_id={session['id']}")
      user_bookings=cursor.fetchall()
      booking_id=''
      movie_name=''
      theater_name=''
      movie_schedule=''
      seats_booked=''
      total_cost=''
      count_2=0
    
      for books in user_bookings:
          if count_2==0:
              booking_id=books[0]
              movie_name=books[1]
              theater_name=books[2]
              movie_schedule=books[3]
              seats_booked=books[4]
              total_cost=books[5]
              count_2=1
          else:
              booking_id=str(booking_id)+','+str(books[0])
              movie_name=movie_name+','+books[1]
              theater_name=theater_name+','+books[2]
              movie_schedule=str(movie_schedule)+','+str(books[3])
              seats_booked=str(seats_booked)+','+str(books[4])
              total_cost=str(total_cost)+','+str(books[5])

           

      return render_template('user_dashboard.html',booking_id=booking_id,movie_name=movie_name,theater_name=theater_name,movie_schedule=movie_schedule,seats_booked=seats_booked,total_cost=total_cost,current_time=str(dt.now()))

    except Exception as e:
        raise e



if __name__ == "__main__":
    app.run()
    
