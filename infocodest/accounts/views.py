from flask import flash, redirect, render_template, request, url_for, abort
from flask_login import login_required, login_user, logout_user, current_user

from infocodest.accounts import accounts_bp
from infocodest.accounts.forms import LoginForm, RegisterForm, PasswordForm

from infocodest.services import AuthService


@accounts_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        flash("You are already registered.", "info")
        return redirect(url_for("home.home"))

    form = RegisterForm(request.form)
    if form.validate_on_submit():
        auth_service = AuthService()
        success, user, error = auth_service.register_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )

        if success:
            logout_user()
            flash("Account created successfully.", "info")
            return render_template(
                "accounts/register.html",
                msg="Account created successfully.",
                success=True,
                form=form
            )
        else:
            flash(error, "danger")
            return render_template(
                "accounts/register.html",
                msg=error,
                success=False,
                form=form
            )

    return render_template("accounts/register.html", msg="", success=False, form=form)


@accounts_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        flash("You are already logged in.", "info")
        return redirect(url_for("home.home"))

    form = LoginForm(request.form)
    if form.validate_on_submit():
        auth_service = AuthService()
        user = auth_service.authenticate_user(
            username=form.username.data,
            password=form.password.data
        )

        if user:
            login_user(user, remember=form.remember.data)
            print("Logged in successfully.")
            return redirect(url_for("home.home"))
        else:
            flash("Invalid username and/or password.", "danger")
            return render_template("accounts/login.html",
                                 form=form,
                                 msg="Wrong user or password")

    return render_template("accounts/login.html", form=form)


# @accounts_bp.route("/password")
# def password():
#     return render_template("accounts/password.html")


@accounts_bp.route("/password", methods=["GET", "POST"])
def password():
    form = PasswordForm()
    if form.validate_on_submit():
        return render_template("accounts/recuperar.html", msg="Se ha enviado un correo a {} para recuperar password.".format(form.email.data))
    return render_template("accounts/password_wtf.html", form=form)


@accounts_bp.route("/user/<username>")
def user(username):
    auth_service = AuthService()
    user = auth_service.get_user_by_username(username)

    if not user:
        abort(404)

    return render_template("accounts/user.html", user=user)


@accounts_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You were logged out.", "success")
    return redirect(url_for("accounts.login"))
