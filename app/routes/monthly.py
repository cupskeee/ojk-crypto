import os
from datetime import datetime, timedelta
from io import BytesIO

from flask import render_template, flash, jsonify, send_file, request
from openpyxl import load_workbook

from app.forms import SubmitMonthlyReportGenerationForm
from app.routes import monthly
from app.models import Settings
from app.utils.decorator import login_required
from app.utils.monthly_report_generator import (
    generate_customer_growth_report,
    generate_top20_customers_by_transaction_value,
    generate_top20_customers_by_topup_value,
    generate_top20_customers_by_withdrawal_value
)
from app.utils.xlsx_handler import (
    fill_daily_report,
    fill_monthly_report
)


def _prepare_date_range(selected_month):
    """Helper function to prepare date ranges for reports."""
    start_date = selected_month.replace(day=1)
    end_date = (start_date + timedelta(days=31)).replace(day=1) - timedelta(days=1)
    # Adjust end_date to the last timestamp of the month
    end_date = datetime.combine(end_date, datetime.max.time())
    return start_date, end_date


def _generate_report_data(start_date, end_date):
    """Helper function to generate all report data."""
    customer_growth = generate_customer_growth_report(start_date, end_date)
    top_20_transaction = generate_top20_customers_by_transaction_value(start_date, end_date)
    top_20_topup = generate_top20_customers_by_topup_value(start_date, end_date)
    top_20_withdrawal = generate_top20_customers_by_withdrawal_value(start_date, end_date)
    # Add other report generation functions here as needed
    return customer_growth, top_20_transaction, top_20_topup, top_20_withdrawal


@monthly.route('', methods=['GET'])
@login_required
def index():
    """Render the monthly report generation form."""
    return render_template('monthly.html', form=SubmitMonthlyReportGenerationForm())


@monthly.route('/generate', methods=['POST'])
@login_required
def generate():
    """Generate monthly reports based on selected date."""
    form = SubmitMonthlyReportGenerationForm()
    if not form.validate_on_submit():
        return render_template('monthly.html', form=form)

    selected_month = form.month.data
    selected_date = datetime.strptime(selected_month, '%Y-%m')
    start_date, end_date = _prepare_date_range(selected_date)

    if form.submit.data:
        lkbpakd, lrtthp, lrttopa, lrtnwda = _generate_report_data(start_date, end_date)
        flash('Monthly report generated successfully!')
        return render_template('monthly.html', form=form, lkbpakd=lkbpakd, lrtthp=lrtthp, lrttopa=lrttopa,
                               lrtnwda=lrtnwda)
    elif form.generate.data:
        settings = {setting.key: setting.value for setting in Settings.query.all()}
        lkbpakd, lrtthp, lrttopa, lrtnwda = _generate_report_data(start_date, end_date)

        # Create and fill the Excel report
        xlsx_template = 'app/static/monthly_template.xlsx'
        workbook = load_workbook(filename=xlsx_template)
        workbook = fill_monthly_report(workbook, settings, lkbpakd, lrtthp, lrttopa, lrtnwda, end_date)

        # Prepare the file for download
        output = BytesIO()
        workbook.save(output)
        output.seek(0)
        filename = f"monthly_report_{selected_month}.xlsx"

        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )