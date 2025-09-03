from flask import Flask, render_template, request, redirect, url_for, flash
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import re
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Email, Length
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv


app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'default_secret_key')
csrf = CSRFProtect(app)

# Configure your email settings using environment variables
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_RECEIVER = os.environ.get('EMAIL_RECEIVER')

# Flask-WTF form for contact
class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    subject = StringField('Subject', validators=[DataRequired(), Length(max=100)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(max=1000)])


@app.route('/', methods=['GET'])
def index():
    form = ContactForm()
    return render_template('portfolio-fixed.html', form=form)


@app.route('/contact', methods=['POST'])
def contact():
    form = ContactForm()
    if not form.validate_on_submit():
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}", 'error')
        return redirect(url_for('index'))

    name = form.name.data.strip()
    email = form.email.data.strip()
    subject = form.subject.data.strip()
    message = form.message.data.strip()

    # Compose email
    msg = MIMEMultipart()
    msg['From'] = EMAIL_HOST_USER
    msg['To'] = EMAIL_RECEIVER
    msg['Subject'] = f"Portfolio Contact: {subject}"
    body = f"Name: {name}\nEmail: {email}\nSubject: {subject}\nMessage:\n{message}"
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        server.sendmail(EMAIL_HOST_USER, EMAIL_RECEIVER, msg.as_string())
        server.quit()
        flash('Message sent successfully!', 'success')
    except Exception as e:
        flash(f'Error sending message: {str(e)}', 'error')

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)