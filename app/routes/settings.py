from flask import render_template, flash
from app import db
from app.routes import settings
from app.utils.decorator import login_required
from app.forms import UpdateSettingsForm
from app.models import Settings

@settings.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = UpdateSettingsForm()
    if form.validate_on_submit():
        settings_keys = form.get_filled_fields()
        settings = Settings.query.filter(Settings.key.in_(settings_keys.keys())).all()
        for setting in settings:
            if setting.key in settings_keys:
                setting.value = settings_keys[setting.key]
        db.session.commit()
        flash("Settings updated successfully!", "success")
    settings = Settings.query.all()
    for setting in settings:
        if setting.key in form._fields:
            form._fields[setting.key].data = setting.value
    return render_template('setting.html', form=form)
