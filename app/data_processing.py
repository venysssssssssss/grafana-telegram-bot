import time

import duckdb
import pandas as pd


class DataProcessor:
    def __init__(self, file_path):
        self.file_path = file_path

    def analyze_data(self):
        df = pd.read_csv(self.file_path, sep=',', skiprows=1)
        print(df)

        if 'Status' not in df.columns:
            df.columns = (
                df.columns.str.strip()
            )  # Remove any leading/trailing whitespace
            if 'Status' not in df.columns:
                raise ValueError(
                    "The 'Status' column is not present in the CSV file."
                )

        df = df[df['P'] == 1]
        if df.empty:
            return 'no_data'

        falha_detectada = self.apply_business_rules(df)

        con = duckdb.connect(database=':memory:')
        con.register('data', df)
        total_rows = con.execute('SELECT COUNT(*) FROM data').fetchone()[0]
        count_success = con.execute(
            "SELECT COUNT(*) FROM data WHERE Status = 'Concluído com sucesso'"
        ).fetchone()[0]
        count_business_error = con.execute(
            "SELECT COUNT(*) FROM data WHERE Status = 'Erro de negócio'"
        ).fetchone()[0]
        count_system_failure = con.execute(
            "SELECT COUNT(*) FROM data WHERE Status = 'Falha de sistema'"
        ).fetchone()[0]
        print(f'total_rows: {total_rows}')
        print(f'count_success: {count_success}')
        print(f'count_business_error: {count_business_error}')
        print(f'count_system_failure: {count_system_failure}')

        return {
            'total_rows': total_rows,
            'count_success': count_success,
            'count_business_error': count_business_error,
            'count_system_failure': count_system_failure,
            'falha_detectada': falha_detectada,
        }

    def apply_business_rules(self, df):
        for row in range(1, min(4, len(df))):
            if (
                df.iloc[row]['Item'] == 'ValidarVendasLiberadas'
                and df.iloc[row]['Status'] == 'Falha de sistema'
            ):
                return True
        return False
