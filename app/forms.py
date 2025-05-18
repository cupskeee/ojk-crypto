import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, ValidationError
from wtforms.validators import DataRequired, Optional, Regexp


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

class SubmitDailyReportGenerationForm(FlaskForm):
    date = DateField('Select Date', validators=[DataRequired()])
    submit = SubmitField('Show Data')
    generate = SubmitField('Download Data')

    def validate_date(self, field):
        today = datetime.date.today()
        if field.data > today:
            raise ValidationError('You cannot select a future date.')
        if field.data == today:
            raise ValidationError('You cannot select today\'s date.')


class SubmitMonthlyReportGenerationForm(FlaskForm):
    month = StringField('Select Month', validators=[
        DataRequired(),
        Regexp('^[0-9]{4}-[0-9]{2}$', message='Format must be YYYY-MM')
    ])
    submit = SubmitField('Show Data')
    generate = SubmitField('Download Data')

    def validate_month(self, field):
        try:
            # Parse the YYYY-MM string to a date object (day defaults to 1)
            date_value = datetime.datetime.strptime(field.data, '%Y-%m').date()
            today = datetime.date.today()

            if date_value.year > today.year or (date_value.year == today.year and date_value.month > today.month):
                raise ValidationError('You cannot select a future month.')
            if date_value.month == today.month and date_value.year == today.year:
                raise ValidationError('You cannot select this month.')
        except ValueError:
            raise ValidationError('Invalid month format. Use YYYY-MM.')



class UpdateSettingsForm(FlaskForm):
    company_code = StringField('Company Code', validators=[DataRequired()])
    company_name = StringField('Company Name', validators=[DataRequired()])
    company_address = StringField('Company Address', validators=[DataRequired()])
    director_name = StringField('Director Name', validators=[DataRequired()])
    director_position = StringField('Director Position', validators=[DataRequired()])
    submit = SubmitField('Save Settings')

    def get_filled_fields(self):
        filled_fields = {}
        for field_name, field in self._fields.items():
            if field.data:
                filled_fields[field_name] = field.data
        return filled_fields
