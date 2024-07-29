import pandas as pd
import duckdb

def analyze_data(file_path):
    # Read the CSV file into a pandas DataFrame, skipping the first row if necessary
    df = pd.read_csv(file_path, sep=',', skiprows=1)

    # Verify the column names
    column_names = df.columns.tolist()
    print("Column names in the CSV file:", column_names)

    # Filter the DataFrame to include only rows where column 'P' is 1
    df = df[df['P'] == 1]

    # Check if the "Status" column exists and rename columns if necessary
    if 'Status' not in df.columns:
        df.columns = df.columns.str.strip()  # Remove any leading/trailing whitespace
        if 'Status' not in df.columns:
            raise ValueError("The 'Status' column is not present in the CSV file.")

    # Create a DuckDB connection and register the DataFrame
    con = duckdb.connect(database=':memory:')
    con.register('data', df)

    # Example queries to extract KPIs
    total_rows = con.execute("SELECT COUNT(*) FROM data").fetchone()[0]
    count_success = con.execute("SELECT COUNT(*) FROM data WHERE Status = 'Concluído com sucesso'").fetchone()[0]
    count_business_error = con.execute("SELECT COUNT(*) FROM data WHERE Status = 'Erro de negócio'").fetchone()[0]
    count_system_failure = con.execute("SELECT COUNT(*) FROM data WHERE Status = 'Falha de sistema'").fetchone()[0]

    print(f'Total de linhas processadas: {total_rows}')
    print(f'Sucessos: {count_success}')
    print(f'Erros de negócio: {count_business_error}')
    print(f'Falhas de sistema: {count_system_failure}')

    return {
        "total_rows": total_rows,
        "count_success": count_success,
        "count_business_error": count_business_error,
        "count_system_failure": count_system_failure
    }
