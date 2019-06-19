# Metadata
#=========
__author__ = 'Luis Domingues'

# Description
#============
# Library that provides sqlite operations

# Notes
#======
# This library assumes a previous filtering of the user_input has occurred

# Known issues/enhancements
#==========================
# Go through lib_sql and protect the functions against potential errors (trying to insert a column name that already exists). The best way to go may be to create function that filters what the user is inputing, rather than protect the functions themselves.
# Make the delete column function (https://www.sqlite.org/faq.html#q6)

#----------------------------------------------------------------------------------------
# IMPORTS
#----------------------------------------------------------------------------------------
import sqlite3 as lib_sql
import lib_path_ops as lib_path
import lib_file_ops as lib_file
import sys



#----------------------------------------------------------------------------------------
# INPUTS
#----------------------------------------------------------------------------------------
root_path = lib_path.get_root_path(lib_path.get_abs_path(""),"./libraries")
database_path = lib_path.join_paths(root_path, "databases")




#----------------------------------------------------------------------------------------
# FUNCTIONS
#----------------------------------------------------------------------------------------
def connect_to_database(database_path, database_name):
    """
    Function that connects to a database and returns the connection and cursor objects
    """
    try:
        database_name = database_name + ".db"
        path = lib_path.join_paths(database_path,database_name)
        con = lib_sql.connect(path)
        cur = con.cursor()
    except lib_sql.Error:
        print("Could not connect to database <%s>." % path)
        sys.exit(1)
    return [con, cur]


def close_database(con):
    """
    Function that closes a connection to a database
    """
    if con:
        con.close()
        return 0
    else:
        print("Could not close database <%s>." % str(con))
        return 1


def delete_database(path):
    """
    Function that deletes a database
    """
    if path:
        lib_file.delete_file(path)
        return 0
    else:
        print("Could not delete database <%s>." % path)
        return 1


def create_table(con, table_name):
    """
    Function that creates a table with a given table name.
    """
    delete_table(con, "dummy_dummy") # delete it if already exists
    cur = con.cursor()
    cur.execute("CREATE TABLE dummy_dummy(rID INTEGER PRIMARY KEY)") # Need to create a dummy because there is only a rename command
    execute_string = "ALTER TABLE dummy_dummy RENAME TO " + table_name
    cur.execute(execute_string)
    con.commit()
    return 0


def delete_table(con, table_name):
    """
    Function that deletes a table with a given table name.
    """
    cur = con.cursor()
    execute_string = "DROP TABLE IF EXISTS " + table_name
    cur.execute(execute_string)
    con.commit()
    return 0


def create_row(con, table_name):
    """
    Function that inserts a new row in a table.
    """
    cur = con.cursor()
    execute_string = "INSERT INTO " + table_name + " DEFAULT VALUES"
    cur.execute(execute_string)
    con.commit()
    return 0


def insert_row(con, table_name, row_tuple):
    """
    Function that inserts a row in a table.
    """
    cur = con.cursor()
    Ncol = get_table_total_columns(con, table_name)
    s_aux = "(" + "?,"*Ncol + ")"
    s = s_aux.replace(",)",")") # getting the parameterised string with size of Ncol
    execute_string = "INSERT INTO " + table_name + " VALUES" + s
    cur.execute(execute_string, row_tuple)
    con.commit()
    return 0


def delete_row(con, table_name, rID):
    """
    Function that deletes a row from a table.
    """
    cur = con.cursor()
    execute_string = "DELETE FROM " + table_name + " WHERE rID=" + str(rID)
    cur.execute(execute_string)
    con.commit()
    return 0


def get_last_row_id(con, table_name):
    """
    Function that returns the last row id for a table with table_name
    """
    cur = con.cursor()
    execute_string = "SELECT max(ROWID) FROM " + table_name
    cur.execute(execute_string) # Since rID is an INTEGER PRIMARY KEY it is an alias for ROWID (always exists for numbered tables)
    last_rID = cur.fetchone()[0]
    return last_rID


def get_row_id_from_column_name_and_value(con, table_name, column_name, value):
    """
    Function that returns the rID(s) of a given element as a list.
    Note: the value can appear in more than one row for the same column name
    """
    cur = con.cursor()
    execute_string = "SELECT rID FROM " + table_name + " WHERE " + column_name + "=" + value
    cur.execute(execute_string)
    rows = cur.fetchall()
    rID_list = []
    for row in rows:
        rID = row[0]
        rID_list.append(rID)
    return rID_list


def create_column(con, table_name, column_name, column_type):
    """
    Function that adds a column to a given table
    """
    cur = con.cursor()
    execute_string = "ALTER TABLE " + table_name + " ADD COLUMN " + column_name + " " + column_type
    cur.execute(execute_string)
    con.commit()
    return 0


def delete_column(con, table_name):
    """
    Function that deletes a column from a table.
    """
    # FIX
    return 0


def get_column_id(con, table_name, column_name):
    """
    Function that returns the cID of a given columnn name or None if the column name is not found
    """
    metadata_list = get_table_metadata(con, table_name)
    cID = None
    i = 0
    while cID == None and i < len(metadata_list):
        if metadata_list[i][1] == column_name:
            cID = metadata_list[i][0]
        i = i + 1
    return cID


def insert_element(con, table_name, row_id, column_name, value):
    """
    Function that inserts a new element in a table.
    """
    create_row(con, table_name)
    update_element(con, table_name, row_id, column_name, value)
    return 0


def update_element(con, table_name, row_id, column_name, value):
    """
    Function that updates the value of one element in a table
    """
    cur = con.cursor()
    execute_string = "UPDATE " + table_name + " SET " + column_name + "=?" + " WHERE rID=?"
    cur.execute(execute_string, (value, row_id))
    con.commit()
    return 0


def get_database_tables_names(con):
    """
    Function that returns a list of table names for a given database
    """
    cur = con.cursor()
    execute_string = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;"
    cur.execute(execute_string)
    table_tuple_list = cur.fetchall()
    table_list_result = []
    for table in table_tuple_list:
        for name in table:
            table_list_result.append(str(name))
    return table_list_result


def get_table_metadata(con, table_name):
    """
    Function that gets the info about a table's column names and types
    """
    cur = con.cursor()
    execute_string = "PRAGMA table_info(" + table_name + ")"
    cur.execute(execute_string)
    metadata_tuple_list = cur.fetchall()
    metadata_list_result = []
    for t in metadata_tuple_list:
        #      ID,   Name,      Type,      NotNull, DefaultVal, PrimaryKey
        aux = (t[0], str(t[1]), str(t[2]), t[3],    t[4],       t[5])
        metadata_list_result.append(aux)
    return metadata_list_result


def get_table_total_rows(con, table_name):
    """
    Function that returns the total number of rows in a given table
    """
    cur = con.cursor()
    execute_string = "SELECT COUNT(*) FROM " + table_name
    cur.execute(execute_string)
    count = cur.fetchall()
    return count[0][0]


def get_table_total_columns(con, table_name):
    """
    Function that returns the total number of columns in a given table
    """
    metadata_list = get_table_metadata(con, table_name)
    return len(metadata_list)


def get_table_rows(con, table_name):
    """
    Function that returns the rows as a tuple list for a given table
    """
    cur = con.cursor()
    execute_string = "SELECT * FROM " + table_name
    cur.execute(execute_string)
    rows_tuple_list = cur.fetchall()
    return rows_tuple_list


def get_row_id_from_row(row_tuple):
    """
    Function that returns the rID of a given row_tuple
    """
    return row_tuple[0]


def get_table_rows_ids(con, table_name):
    """
    Function that returns the rows as a tuple list for a given table
    """
    rID_list = []
    rows_tuple_list = get_table_rows(con ,table_name)
    for row_tuple in rows_tuple_list:
        rID = get_row_id_from_row(row_tuple)
        rID_list.append(rID)
    return rID_list


def get_table_column_names(con, table_name):
    """
    Function that returns the column names list for a given table
    """
    metadata_tuple_list = get_table_metadata(con, table_name)
    column_names_list_result = []
    for column_tuple in metadata_tuple_list:
        column_name = str(column_tuple[1])
        column_names_list_result.append(column_name)
    return column_names_list_result


def print_table_metadata(con, table_name):
    """
    Function that prints the metadata of a given table
    """
    metadata_tuple_list = get_table_metadata(con, table_name)
    print("\nColumn Info:\nID, Name, Type, NotNull, DefaultVal, PrimaryKey")
    for col in metadata_tuple_list:
        print(col)
    return 0


def print_table_rows(con, table_name):
    """
    Function that prints the table rows
    """
    rows_tuple_list = get_table_rows(con, table_name)
    print("\nRows:")
    for row in rows_tuple_list:
        print(row)
    return 0


def print_database_tables_names(con):
    """
    Function that prints the database tables
    """
    tables_name_list = get_database_tables_names(con)
    for table_name in tables_name_list:
        print(table_name)
    return 0


#----------------------------------------------------------------------------------------
# MAIN
#----------------------------------------------------------------------------------------
if __name__ == "__main__":
    [con, cur] = connect_to_database(database_path, "user_data")
    delete_table(con, "test")
    create_table(con, "test")
    delete_table(con, "bla")
    create_table(con,"bla")
    create_column(con, "test", "Name", "TEXT")
    insert_element(con, "test", 1, "Name", "Ines")
    insert_element(con, "test", 2, "Name", "Margarida")
    insert_element(con, "test", 3, "Name", "Pilar")
    update_element(con, "test", 1, "Name", "Luis")
    insert_row(con,"test",(4, u'Luis'))
    delete_row(con,"test",2)

    # Print
    print_table_metadata(con, "test")
    print_table_rows(con,"test")
    print(get_column_id(con, "test", "Name"))
    print(get_last_row_id(con, "test"))
    print(get_row_id_from_column_name_and_value(con, "test", "Name", "'Pilar'"))
    print(get_database_tables_names(con))
    print(get_table_total_rows(con, "test"))
    print(get_table_column_names(con, "test"))
    print(get_row_id_from_column_name_and_value(con, "test", "Name", "'Luis'"))
    print(get_row_id_from_row((4, u'Luis')))

    # Close database
    close_database(con)

    pass