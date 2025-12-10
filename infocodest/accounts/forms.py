from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length

from infocodest.models.users import User

class PasswordForm(FlaskForm):
    email = EmailField("Email Adress", id="email_create", validators=[DataRequired(), Email()])
    submit = SubmitField("Reset Password")


class LoginForm(FlaskForm):
    username = StringField("Username", id="username_login", validators=[DataRequired()])
    password = PasswordField("Password", id="pwd_login", validators=[DataRequired()])
    remember = BooleanField("Remember Password")
    submit = SubmitField("Login")


class RegisterForm(FlaskForm):
    username = StringField(
        "Username",
        id="username_create",
        validators=[DataRequired(), Length(min=4, max=25)],
    )
    email = EmailField(
        "Email Adress", id="email_create", validators=[DataRequired(), Email()]
    )
    password = PasswordField("Password", id="pwd_create", validators=[DataRequired(), Length(8, 72)])
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            Length(8, 72),
            EqualTo("password", message="Passwords must match."),
        ],
    )
    submit = SubmitField("Create Account")


    def validate(self, extra_validators=None):
        initial_validation = super(RegisterForm, self).validate(extra_validators)
        if not initial_validation:
            return False
        user = User.query.filter_by(username=self.username.data).first()
        if user is not None:
            self.username.errors.append("Username already registered.")
            return False
        user = User.query.filter_by(email=self.email.data).first()
        if user is not None:
            self.email.errors.append("Please use a different email address.")
            return False
        if self.password.data != self.confirm_password.data:
            self.password.errors.append("Passwords must match.")
            return False
        return True
