from openpyxl import Workbook
from datetime import datetime




def fill_monthly_report(workbook: Workbook, settings, lkbpakd, lrtthp, lrttopa, lrtnwda, report_date):
    """
    Fill the monthly report template with data.

    Args:
        workbook (Workbook): The Excel workbook to fill.
        settings (dict): Settings for filling the report.
        lkbpakd (dict): Data for the LKBPAKD sheet.
        lrtthp (list): Data for the LRTTHP sheet.
        lrttopa (list): Data for the LRTTOPA sheet.
        lrtnwda (list): Data for the LRTNWDA sheet.
        report_date (datetime): The date for the report.
    """
    # ------- Data Umum ----- #
    data_umum = workbook["Data Umum"]
    data_umum['D5'] = datetime.now().strftime("%d-%b-%Y")
    data_umum['D6'] = settings.get('company_code')
    data_umum['D7'] = settings.get('company_name')
    data_umum['D8'] = settings.get('company_address')
    data_umum['D11'] = report_date.strftime("%d-%b-%Y")
    data_umum['D15'] = settings.get('director_name')
    data_umum['D16'] = settings.get('director_position')

    # ------- LKBPAKD ----- #
    lkbpakd_sheet = workbook["LKBPAKD"]
    lkbpakd_sheet['E16'] = lkbpakd["starting_customers"]["Domestik"]["individual"]
    lkbpakd_sheet['F16'] = lkbpakd["starting_customers"]["Asing"]["individual"]
    lkbpakd_sheet['G16'] = lkbpakd["starting_customers"]["Domestik"]["corporate"]
    lkbpakd_sheet['H16'] = lkbpakd["starting_customers"]["Asing"]["corporate"]
    lkbpakd_sheet['E17'] = lkbpakd["new_customers"]["Domestik"]["individual"]
    lkbpakd_sheet['F17'] = lkbpakd["new_customers"]["Asing"]["individual"]
    lkbpakd_sheet['G17'] = lkbpakd["new_customers"]["Domestik"]["corporate"]
    lkbpakd_sheet['H17'] = lkbpakd["new_customers"]["Asing"]["corporate"]
    lkbpakd_sheet['E18'] = lkbpakd["exiting_customers"]["Domestik"]["individual"]
    lkbpakd_sheet['F18'] = lkbpakd["exiting_customers"]["Asing"]["individual"]
    lkbpakd_sheet['G18'] = lkbpakd["exiting_customers"]["Domestik"]["corporate"]
    lkbpakd_sheet['H18'] = lkbpakd["exiting_customers"]["Asing"]["corporate"]
    lkbpakd_sheet['E19'] = lkbpakd["ending_customers"]["Domestik"]["individual"]
    lkbpakd_sheet['F19'] = lkbpakd["ending_customers"]["Asing"]["individual"]
    lkbpakd_sheet['G19'] = lkbpakd["ending_customers"]["Domestik"]["corporate"]
    lkbpakd_sheet['H19'] = lkbpakd["ending_customers"]["Asing"]["corporate"]

    # ------- LRTTHP ----- #
    lrtthp_sheet = workbook["LRTTHP"]
    for i, data in enumerate(lrtthp):
        lrtthp_sheet[f'E{i + 16}'] = data['identification_type']
        lrtthp_sheet[f'F{i + 16}'] = data['identification_number']
        lrtthp_sheet[f'G{i + 16}'] = data['name']
        lrtthp_sheet[f'H{i + 16}'] = data['citizenship']
        lrtthp_sheet[f'I{i + 16}'] = data['customer_type']
        lrtthp_sheet[f'J{i + 16}'] = data['total_transaction_value']

    # ------- LRTTOPA ----- #
    lrttopa_sheet = workbook["LRTTOPA"]
    for i, data in enumerate(lrttopa):
        lrttopa_sheet[f'E{i + 16}'] = data['identification_type']
        lrttopa_sheet[f'F{i + 16}'] = data['identification_number']
        lrttopa_sheet[f'G{i + 16}'] = data['name']
        lrttopa_sheet[f'H{i + 16}'] = data['citizenship']
        lrttopa_sheet[f'I{i + 16}'] = data['customer_type']
        lrttopa_sheet[f'J{i + 16}'] = data['total_transaction_value']

    # ------- LRTNWDA ----- #
    lrtnwda_sheet = workbook["LRTNWDA"]
    for i, data in enumerate(lrtnwda):
        lrtnwda_sheet[f'E{i + 16}'] = data['identification_type']
        lrtnwda_sheet[f'F{i + 16}'] = data['identification_number']
        lrtnwda_sheet[f'G{i + 16}'] = data['name']
        lrtnwda_sheet[f'H{i + 16}'] = data['citizenship']
        lrtnwda_sheet[f'I{i + 16}'] = data['customer_type']
        lrtnwda_sheet[f'J{i + 16}'] = data['total_transaction_value']

    return workbook


def fill_daily_report(workbook: Workbook, settings, ltakdk, lrtak, lstakdkp, lsdk, report_date, cutoff_date):
    """
    Fill the daily report template with data.

    Args:
        workbook (Workbook): The Excel workbook to fill.
        settings (dict): Settings for filling the report.
        ltakdk (dict): Data for the LTAKDK sheet.
        lrtak (list): Data for the LRTAK sheet.
        lstakdkp (list): Data for the LSTAKDKP sheet.
        lsdk (list): Data for the LSDK sheet.
        report_date (datetime): The date for the report.
    """
    # ------- Data Umum ----- #
    data_umum = workbook["Data Umum"]
    data_umum['D5'] = datetime.now().strftime("%d-%b-%Y")
    data_umum['D6'] = settings.get('company_code')
    data_umum['D7'] = settings.get('company_name')
    data_umum['D8'] = settings.get('company_address')
    data_umum['D11'] = cutoff_date.strftime("%d-%b-%Y")
    data_umum['D15'] = settings.get('director_name')
    data_umum['D16'] = settings.get('director_position')

    # ------- LSDK ----- #
    lsdk_sheet = workbook["LSDK"]
    lsdk_sheet['E16'] = lsdk[0]['previous_balance']
    lsdk_sheet['F16'] = lsdk[0]['topup']
    lsdk_sheet['G16'] = lsdk[0]['withdrawal']
    lsdk_sheet['F17'] = lsdk[1]['topup']
    lsdk_sheet['G17'] = lsdk[1]['withdrawal']

    # ------- LSTAKDKP ----- #
    lstakdkp_sheet = workbook["LSTAKDKP"]
    if len(lstakdkp) <= 100:
        for i, data in enumerate(lstakdkp):
            lstakdkp_sheet[f'E{i + 16}'] = data['symbol']
            lstakdkp_sheet[f'F{i + 16}'] = data['name']
            lstakdkp_sheet[f'I{i + 16}'] = 0
            lstakdkp_sheet[f'J{i + 16}'] = data['akd_konsumen_pedagang']
            lstakdkp_sheet[f'K{i + 16}'] = data['akd_konsumen_penyimpanan']
            lstakdkp_sheet[f'L{i + 16}'] = data['price']

    # ------- LTAKDK ----- #
    ltakdk_sheet = workbook["LTAKDK"]
    ltakdk_sheet['G16'] = ltakdk["Asing"]["individual"]["buy"]
    ltakdk_sheet['H16'] = ltakdk["Domestik"]["individual"]["buy"]
    ltakdk_sheet['G17'] = ltakdk["Asing"]["corporate"]["buy"]
    ltakdk_sheet['H17'] = ltakdk["Domestik"]["corporate"]["buy"]
    ltakdk_sheet['G19'] = ltakdk["Asing"]["individual"]["sell"]
    ltakdk_sheet['H19'] = ltakdk["Domestik"]["individual"]["sell"]
    ltakdk_sheet['G20'] = ltakdk["Asing"]["corporate"]["sell"]
    ltakdk_sheet['H20'] = ltakdk["Domestik"]["corporate"]["sell"]
    ltakdk_sheet['G22'] = ltakdk["Asing"]["corporate"]["buy"] + ltakdk["Asing"]["corporate"]["sell"] + \
                          ltakdk["Asing"]["individual"]["buy"] + ltakdk["Asing"]["individual"]["sell"]
    ltakdk_sheet['H22'] = ltakdk["Domestik"]["corporate"]["buy"] + ltakdk["Domestik"]["corporate"]["sell"] + \
                          ltakdk["Domestik"]["individual"]["buy"] + ltakdk["Domestik"]["individual"]["sell"]

    # ------- LRTAK ----- #
    lrtak_sheet = workbook["LRTAK"]
    for i, data in enumerate(lrtak):
        lrtak_sheet[f'E{i + 16}'] = data['symbol']
        lrtak_sheet[f'F{i + 16}'] = data['name']
        lrtak_sheet[f'G{i + 16}'] = data['min_price']
        lrtak_sheet[f'H{i + 16}'] = data['max_price']
        lrtak_sheet[f'I{i + 16}'] = data['transaction_frequency']
        lrtak_sheet[f'J{i + 16}'] = data['total_volume']
        lrtak_sheet[f'K{i + 16}'] = data['total_value']

    return workbook
