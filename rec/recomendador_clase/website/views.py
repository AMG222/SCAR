from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def choose():
    if request.method == 'POST':
        choosed = request.form.get('button')
        if choosed=="Demographic":
            return redirect(url_for('viewsd.home'))
        elif choosed=="Colaborative":
            return redirect(url_for('viewsc.home'))
        else:
            return redirect(url_for('viewsm.home'))
    return render_template("choose.html", user=current_user)