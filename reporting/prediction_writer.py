import xlsxwriter
from reporting.prediction_instance import PredictionInstance as PI
from typing import List

#TODO: basically this

title_format_dict = {
    'font_name': 'Calibri',
    'font_size': 14,
    'bottom': 1
}

section_title_format_dict = {
    'font_name': 'Calibri',
    'font_size': 14,
    'bottom': 2,
    'bold': True
}

string_title_format_dict = {
    'font_name': 'Calibri',
    'font_size': 11,
    'bottom': 1,
    'align': 'left',
    'valign': 'vcenter'
}

numerical_title_format_dict = {
    'font_name': 'Calibri',
    'font_size': 11,
    'bottom': 1,
    'align': 'right',
    'valign': 'vcenter'
}

def write_predictions(prediction_instance:List[PI],
                        has_products = False,
                        workbook_title:str = 'workBook.xlsx'):
    
    if has_products:
        num_cols = 10
    else:
        num_cols = 9
    workbook = xlsxwriter.Workbook(workbook_title)
    overview_worksheet = workbook.add_worksheet('Overview')
    # customer_worksheet = workbook.add_worksheet('Customer Overview')

    title_format = overview_worksheet.add_format(title_format_dict)

    section_title_format = overview_worksheet.add_format(section_title_format_dict)

    string_title_format = overview_worksheet.add_format(string_title_format_dict)

    numerical_title_format = overview_worksheet.add_format(numerical_title_format_dict)

    # Take care of the titles etc.
    overview_worksheet.write('A1','Prediction Overview',title_format)

    # TODO: data. Do alternating BG, if above is same don't repeat etc, B/S colors etc.
    # TODO: column sizing (some are smaller than others!)

    # Create a format to use in the merged range.
    # merge_format = workbook.add_format({
    #     'bold': 1,
    #     'border': 1,
    #     'align': 'center',
    #     'valign': 'vcenter',
    #     'fg_color': 'yellow'})


    # # Merge 3 cells.
    # worksheet.merge_range('B4:D4', 'Merged Range', merge_format)


