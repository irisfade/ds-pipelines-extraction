import sqlite3

def setup_db():
    with sqlite3.connect("trackers.db") as db:
        cursor = db.cursor()
        query = """
        CREATE TABLE IF NOT EXISTS Training_Runs (
          id INTENGER PRIMARY KEY, 
          model_id INTEGER
        )
        """
        cursor.executescript(query)
        query = """
        CREATE TABLE IF NOT EXISTS Models (
        id INTEGER PRIMARY KEY
        )
        """
        cursor.executescript(query)
        query = """
        CREATE TABLE IF NOT EXISTs Hyperparameters (
        name TEXT, 
        value TEXT, 
        expr_id INTEGER, 
        times INTEGER,
        run_id INTEGER,
        PRIMARY KEY (name, expr_id, run_id, times)
        )
        """
        cursor.executescript(query)
        query = """
        CREATE TABLE IF NOT EXISTS Outputs (
        run_id INTEGER, 
        name TEXT, 
        line_number TEXT, 
        value TEXT,
        PRIMARY KEY (run_id, name, line_number)
        )
        """
        cursor.executescript(query)
        query = """
           CREATE TABLE IF NOT EXISTS Plots (
           run_id INTEGER PRIMARY KEY, 
           graph_file TEXT,
           value BLOB
           )
          """
        cursor.executescript(query)

        query = """
               CREATE TABLE IF NOT EXISTS Expressions (
               operator TEXT, 
               name TEXT,
               expr_id INTEGER,
               model_id INTEGER,
               PRIMARY KEY (expr_id, model_id)
               )
              """
        cursor.executescript(query)

        query = """
               CREATE TABLE IF NOT EXISTS Edges (
               from_edge INTEGER, 
               to_edge INTEGER,
               model_id INTEGER,
               position  TEXT,
               PRIMARY KEY (from_edge, to_edge, model_id)
               )
              """
        cursor.executescript(query)



def new_training_run(con: sqlite3.Connection, model_id: int)-> int:
    cursor = con.cursor()
    cursor.execute("SELECT MAX(id)+1 FROM Training_Runs")
    (run_id,) = cursor.fetchone()
    cursor.execute("INSERT INTO Training_Runs VALUES(?, ?)", (run_id, model_id))
    con.commit()
    cursor.close()
