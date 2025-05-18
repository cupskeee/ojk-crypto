import os
from datetime import datetime, timedelta
from io import BytesIO

from flask import render_template, flash, jsonify, send_file, request
from openpyxl import load_workbook

from app.forms import SubmitDailyReportGenerationForm
from app.routes import daily
from app.models import Settings
from app.utils.decorator import login_required
from app.utils.daily_report_generator import (
    generate_transactions_by_type_report,
    generate_asset_transaction_report,
    generate_holdings_report,
    generate_topup_withdrawal_report
)
from app.utils.xlsx_handler import fill_daily_report


def _prepare_date_range(selected_date):
    """Helper function to prepare date ranges for reports."""
    start_date = datetime.combine(selected_date, datetime.min.time())
    end_date = datetime.combine(selected_date, datetime.max.time())
    cutoff_date = datetime.combine(selected_date - timedelta(days=1), datetime.max.time())
    return start_date, end_date, cutoff_date


def _generate_report_data(start_date, end_date, cutoff_date):
    """Helper function to generate all report data."""
    ltakdk = generate_transactions_by_type_report(start_date, end_date)
    lrtak = generate_asset_transaction_report(start_date, end_date)
    lstakdkp = generate_holdings_report(cutoff_date)
    lsdk = generate_topup_withdrawal_report(start_date)
    for item in lsdk:
        print(item)

    lsdk_total = {
        'previous_balance': sum(item['previous_balance'] for item in lsdk),
        'topup': sum(item['topup'] for item in lsdk),
        'withdrawal': sum(item['withdrawal'] for item in lsdk),
        'final_balance': sum(item['final_balance'] for item in lsdk)
    }

    return ltakdk, lrtak, lstakdkp, lsdk, lsdk_total


@daily.route('', methods=['GET'])
@login_required
def index():
    """Render the daily report generation form."""
    return render_template('daily.html', form=SubmitDailyReportGenerationForm())


@daily.route('/generate', methods=['POST'])
@login_required
def generate():
    """Generate daily reports based on selected date."""
    form = SubmitDailyReportGenerationForm()
    if not form.validate_on_submit():
        return render_template('daily.html', form=form)

    selected_date = form.date.data
    start_date, end_date, cutoff_date = _prepare_date_range(selected_date)

    try:
        if form.submit.data:
            # Display the report on the page
            ltakdk, lrtak, lstakdkp, lsdk, lsdk_total = _generate_report_data(start_date, end_date, cutoff_date)
            flash('Daily report generated successfully!')
            return render_template(
                'daily.html',
                form=form,
                ltakdk=ltakdk,
                lrtak=lrtak,
                lstakdkp=lstakdkp,
                lsdk=lsdk,
                lsdk_total=lsdk_total
            )

        elif form.generate.data:
            # Generate an Excel file for download
            settings = {setting.key: setting.value for setting in Settings.query.all()}
            ltakdk, lrtak, lstakdkp, lsdk, _ = _generate_report_data(start_date, end_date, cutoff_date)

            # Create and fill the Excel workbook
            xlsx_template = 'app/static/daily_template.xlsx'
            workbook = load_workbook(filename=xlsx_template)
            workbook = fill_daily_report(workbook, settings, ltakdk, lrtak, lstakdkp, lsdk, selected_date, cutoff_date)

            # Prepare the file for download
            output = BytesIO()
            workbook.save(output)
            output.seek(0)

            filename = f"daily_report_{selected_date.strftime('%Y%m%d')}.xlsx"
            return send_file(
                output,
                as_attachment=True,
                download_name=filename,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

    except Exception as e:
        flash(f'Error generating report: {str(e)}', 'error')

    return render_template('daily.html', form=form)


@daily.route('/download', methods=['POST'])
@login_required
def download():
    """Handle downloading of report data."""
    try:
        # Download logic implementation here
        return jsonify({'message': 'Download initiated', 'status': 'success'}), 200
    except Exception as e:
        return jsonify({'message': f'Download failed: {str(e)}', 'status': 'error'}), 500
