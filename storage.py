# storage.py
import sqlite3
import datetime
from typing import List, Optional, Dict, Any, Union

class Storage:
    def __init__(self, db_path: str = "sihteeri.db"):
        """
        Initializes the Storage class with a path to the SQLite database.
        
        Parameters:
            db_path (str): The path to the SQLite database file.
        """
        self.db_path = db_path

    def _connect(self) -> sqlite3.Connection:
        """
        Establishes a connection to the SQLite database.
        
        Returns:
            sqlite3.Connection: A SQLite connection object.
        """
        return sqlite3.connect(self.db_path)

    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[tuple]:
        """
        Executes a given SQL query with optional parameters.
        
        Parameters:
            query (str): The SQL query to execute.
            params (tuple): The parameters for the SQL query, if any.
        
        Returns:
            list: The fetched rows from the database for SELECT queries.
        """
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            conn.commit()
            return cursor.fetchall()

    def insert_data(self, table: str, data: Dict[str, Any], unique_columns: Optional[List[str]] = None) -> Union[int, str]:
        """
        Inserts data into a specified table, checking for duplicates if unique_columns is provided.
        
        Parameters:
            table (str): The name of the table.
            data (dict): A dictionary of column-value pairs to insert.
            unique_columns (list): Optional list of columns to enforce uniqueness.
        
        Returns:
            int or str: The ID of the newly inserted row, or a message if duplicate.
        """
        # Check for duplicates if unique_columns are specified
        if unique_columns:
            where_clause = " AND ".join([f"{col} = ?" for col in unique_columns])
            check_query = f"SELECT id FROM {table} WHERE {where_clause}"
            check_params = tuple(data[col] for col in unique_columns)
            if self.execute_query(check_query, check_params):
                return f"Duplicate entry detected in {table} for {unique_columns}."

        # Insert the data
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, tuple(data.values()))
            conn.commit()
            return cursor.lastrowid

    def fetch_all(self, table: str) -> List[Dict[str, Any]]:
        """
        Fetches all rows from a specified table.
        
        Parameters:
            table (str): The name of the table to fetch rows from.
        
        Returns:
            list: A list of dictionaries representing each row.
        """
        query = f"SELECT * FROM {table}"
        with self._connect() as conn:
            cursor = conn.cursor()
            rows = cursor.execute(query).fetchall()
            column_names = [description[0] for description in cursor.description]
            return [dict(zip(column_names, row)) for row in rows]

    def update_data(self, table: str, data: Dict[str, Any], where_clause: str, where_args: tuple) -> bool:
        """
        Updates data in a specified table based on a condition.
        
        Parameters:
            table (str): The name of the table.
            data (dict): The column-value pairs to update.
            where_clause (str): The WHERE clause for the update.
            where_args (tuple): Arguments for the WHERE clause.
        
        Returns:
            bool: True if any rows were updated, False otherwise.
        """
        columns = ', '.join([f"{col} = ?" for col in data.keys()])
        query = f"UPDATE {table} SET {columns} WHERE {where_clause}"
        
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, tuple(data.values()) + where_args)
            conn.commit()
            return cursor.rowcount > 0

    def create_table(self, schema: dict):
        """
        Creates a table based on the provided schema if it doesn't exist.
        
        Parameters:
            schema (dict): A dictionary defining table structure.
        """
        fields = ', '.join([f"{field} {type}" for field, type in schema["fields"].items()])
        constraints = ', '.join(schema.get("constraints", []))
        query = f"CREATE TABLE IF NOT EXISTS {schema['table']} ({fields} {', ' if constraints else ''}{constraints})"
        self.execute_query(query)

    def fetch_rows_by_date_range(self, table: str, date_column: str, start_date: datetime, end_date: datetime, **conditions):
        """
        Fetches rows where a date column falls within a range and meets additional conditions.
        
        Parameters:
            table (str): Table name.
            date_column (str): The name of the date column to filter.
            start_date (datetime): Start of the date range.
            end_date (datetime): End of the date range.
            conditions (dict): Additional column conditions (e.g., status='pending').

        Returns:
            list: Rows meeting the conditions as dictionaries.
        """
        conditions_query = " AND ".join([f"{col} = ?" for col in conditions.keys()])
        full_query = f"SELECT * FROM {table} WHERE {date_column} BETWEEN ? AND ? {f'AND {conditions_query}' if conditions else ''}"
        params = (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")) + tuple(conditions.values())
        
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(full_query, params)
            rows = cursor.fetchall()
            column_names = [description[0] for description in cursor.description]
            
        return [dict(zip(column_names, row)) for row in rows]

    def list_tables(self) -> List[str]:
        """
        Lists all tables in the database.
        
        Returns:
            list: A list of table names.
        """
        query = "SELECT name FROM sqlite_master WHERE type='table'"
        tables = self.execute_query(query)
        return [table[0] for table in tables]

    def dump_all_tables(self) -> str:
        """
        Dumps the contents of all tables in the database.
        
        Returns:
            str: A formatted string with the contents of all tables.
        """
        tables = self.list_tables()
        output = []
        
        for table in tables:
            output.append(f"Table: {table}")
            rows = self.fetch_all(table)
            if rows:
                for row in rows:
                    output.append(str(row))
            else:
                output.append("  No data found.")
            output.append("\n")
        
        return "\n".join(output)

# Example usage to dump all tables
if __name__ == "__main__":
    storage = Storage()
    print(storage.dump_all_tables())
