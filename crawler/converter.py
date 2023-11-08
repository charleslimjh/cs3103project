import logging
import os.path

import pandas as pd


def convert(dictionary):
    try:
        data_list = [(sport, geo, count) for (sport, geo), count in dictionary.items()]
        df = pd.DataFrame(data_list, columns=['Sport', 'Geolocation', 'Count'])
        filename = 'count_by_geolocation.xlsx'
        # Requires openpyxl module
        df.to_excel(filename, index=False)
        filepath = os.path.join(os.getcwd(),filename)
        logging.info(f"Excel file written at {filepath}")
    except Exception as e:
        logging.exception(f"Error while writing to excel file: {e}")

