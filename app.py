import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect, abort
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Me $ecret$ key U know N0t 0r wi11 NOt fath0m?!'

def get_db_connection():
    conn = sqlite3.connect('BibleIn1Yr.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_readings(read_id):
    conn = get_db_connection()
    reads = conn.execute("""SELECT bid, Date, Reading1, Reading1_Feedback, Reading2, Reading2_Feedback,
                                Reading3, Reading3_Feedback 
                            FROM readings
                            WHERE bid=?""",(read_id,)).fetchone()
    conn.close()
    if reads is None:
        abort(404)
    return reads

# Default index html page
@app.route('/')
def index():
    # Generate default record Id for today's readings
    Today = datetime.today(); curr_yr = Today.year  
    if curr_yr > 2023:
        dn = int(Today.strftime("%j").lstrip("0")) + 31  
    else:
        dn = int(Today.strftime("%j").lstrip("0"))

    conn = get_db_connection()
    reads = conn.execute("""SELECT rowid, Date, Reading1, Reading1_Feedback, Reading2, Reading2_Feedback,
                                Reading3, Reading3_Feedback 
                            FROM readings 
                            WHERE bid = ?""",(dn,)).fetchone()
    conn.close()
    return render_template('index.html', reads=reads)

# Default index html page
@app.route('/<int:ii>')
def index_(ii):
    reads = get_readings(ii)
    if not reads:
        flash("No readings avaialbe for {}!").format(ii)
    else:
        
        conn = get_db_connection()
        reads = conn.execute("""SELECT bid, Date, Reading1, Reading1_Feedback, Reading2, Reading2_Feedback,
                                    Reading3, Reading3_Feedback 
                                FROM readings 
                                WHERE bid = ?""",(ii,)).fetchone()
        conn.close()
        return render_template('index_.html', reads=reads)

# Edit blog post
@app.route('/<int:Id>/edit/', methods=('GET', 'POST'))
def edit(Id):
    reads = get_readings(Id)

    if request.method == 'POST':
        bid = reads['bid']
        dt = reads['Date']
        fb1 = request.form.get('feedback1')
        fb2 = request.form.get('feedback2')
        fb3 = request.form.get('feedback3')

        goback = False
        if not bid:
            flash('bid is required!'); goback = True
        if not dt:
            flash('Date is required!'); goback = True
        if not fb1:
            flash('feedback1 is required!'); goback = True
        if not fb2:
            flash('feedback2 is required!'); goback = True
        if not fb3:
            flash('feedback3 is required!'); goback = True
        if goback:
            flash("goback = True")
            return redirect(url_for('index'))

        else:
            conn = get_db_connection()
            conn.execute("""UPDATE readings 
                            SET Reading1_Feedback = ?, Reading2_Feedback = ?, Reading3_Feedback=?
                            WHERE bid = ?""",
                            (fb1, fb2, fb3, bid))
            message = "%d has been updated." % (bid)
            flash(message)
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('edit.html', reads=reads)
