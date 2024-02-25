from flask import Flask, abort, render_template, redirect, url_for, flash, session, request
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField, TextAreaField, SelectField
from wtforms.validators import DataRequired, URL, Email, Regexp, Length
import smtplib
import datetime as dt
import os
import json
from dotenv import load_dotenv, find_dotenv



app = Flask(__name__)
load_dotenv(find_dotenv())
MY_EMAIL = os.getenv("MY_EMAIL")
MY_PASSWORD = os.getenv("MY_PASSWORD")
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
Bootstrap5(app)


class MessageForm(FlaskForm):
    # Read the JSON file
    with open("country_code.json", "r") as file:
        datas = json.load(file)

    country_codes = [f"{data['name']} ({data['dial_code']})" for data in datas]
    name = StringField("Name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    # country_code = SelectField('Country Code', choices=country_codes, render_kw={"class": "form-control col-md-4"})
    # phone = StringField('Phone', validators=[DataRequired(), Regexp(r'^\d{11}$', message='Invalid phone number.. should not start at 0 or +63')],
    #                     render_kw={"class": "form-control col-md-4"})
    message = TextAreaField("Message", render_kw={"rows": 5, "cols": 11}, validators=[DataRequired()])
    submit = SubmitField("Send Me a Message!")


@app.route("/", methods=['GET', 'POST'])
def home():
    form = MessageForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                with smtplib.SMTP("smtp.gmail.com", 587) as connection:
                    connection.starttls()
                    connection.login(user=MY_EMAIL, password=MY_PASSWORD)
                    connection.sendmail(
                        from_addr=MY_EMAIL,
                        to_addrs=MY_EMAIL,
                        msg=f"Subject: New Message From Portfolio\n\n"
                            f"Name: {form.name.data.title()}\n"
                            f"Email: {form.email.data.strip()}\n"
                            f"Message: {form.message.data}"
                    )
                flash('Your message has been sent successfully!', 'success')
            except Exception as e:
                flash(f'An error occurred: {str(e)}', 'error')
            # Redirect after POST to avoid resubmitting the form on refresh
            return redirect(url_for('home'))
        else:
            # Form validation failed, set a flag to trigger the contact link click
            session['auto_click_contact'] = True

    # Handle the GET request or redirect after POST
    auto_click_contact = session.pop('auto_click_contact', False)
    return render_template("index.html", form=form, auto_click_contact=auto_click_contact)


if __name__ == "__main__":
    app.run(debug=True, port=5009)
