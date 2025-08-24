import datetime
import sqlite3
import csv
from models.Function import Function
import utils
from utils import read_rule_from_line


def init_db(cursor):
    """
    Initializes database.

    Creates empty tables "modules", "function", "arguments", "rules".
    :param cursor: connection cursor
    """
    cursor.execute("DROP TABLE IF EXISTS functions")
    cursor.execute("DROP TABLE IF EXISTS arguments")
    cursor.execute("DROP TABLE IF EXISTS modules")
    cursor.execute("DROP TABLE IF EXISTS rules")
    cursor.execute(
        "CREATE TABLE modules(module_id INTEGER NOT NULL, module_name PRIMARY KEY, version, date)")
    cursor.execute(
        "CREATE TABLE functions(function_id INTEGER PRIMARY KEY, module_name, function_title type UNIQUE, "
        "description, link, FOREIGN KEY(module_name) REFERENCES modules(module_name))")
    cursor.execute(
        "CREATE TABLE arguments(function_id, argument_name, argument_type, argument_position, default_value, "
        "FOREIGN KEY(function_id) REFERENCES functions(function_id))")
    cursor.execute(
        "CREATE TABLE rules(rule_id, rule_name PRIMARY KEY, rule_description, rule, rule_type, added_by_user)")
    cursor.connection.commit()


def init_module(filename, module_name, version, date, cursor):
    with open(filename, newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        header = next(csvreader)
        cursor.execute("SELECT COUNT(*) FROM modules")
        module_id = cursor.fetchall()[0][0] + 1
        # add module info
        cursor.execute("INSERT INTO modules(module_id, module_name, version, date) VALUES(?, ?, ?, ?)",
                       [module_id, module_name, version, date])
        for (index, row) in enumerate(csvreader):
            function = Function.parse_from_list(row)
            # add function values
            cursor.execute("INSERT INTO functions(module_name, function_title, description, link) VALUES(?, ?, ?, ?)",
                           [module_name, function.name, function.description, function.link])
            added_function_id = cursor.lastrowid
            if function.args is not None:
                for arg in function.args:
                    cursor.execute("INSERT INTO arguments VALUES(?, ?, ?, ?, ?)",
                                   [added_function_id, arg.name, arg.type, arg.position, arg.default_value])
    cursor.connection.commit()


def init_rules_from_file(cursor):
    cursor.execute("SELECT COUNT(*) FROM rules")
    added_rule_id = cursor.fetchall()[0][0] + 1
    with open("knowledge_base/rule_base.txt") as file:
        for counter, line in enumerate(file, 1):
            json_rule = read_rule_from_line(line)
            if "name" in json_rule:
                rule_name = json_rule.pop("name")
            if "description" in json_rule:
                rule_desc = json_rule.pop("description")
            if "type" in json_rule:
                rule_type = json_rule.pop("rule_type")
            else:
                rule_type = "syntactic"
            added_by_user = False
            cursor.execute(
                "INSERT INTO rules(rule_id, rule_name, rule_description, rule, rule_type, added_by_user) VALUES(?, ?, ?, ?, ?, ?)",
                [added_rule_id, rule_name, rule_desc, str(json_rule), rule_type, added_by_user])
            added_rule_id = cursor.lastrowid
    cursor.connection.commit()
    pass

def setup_db() -> sqlite3.Connection:
    connection = sqlite3.connect("knowledge_base.db")
    cursor = connection.cursor()
    init_db(cursor)
    date = datetime.date(2023, 1, 17)
    init_module("knowledge_base/pandas 2023-1-17 1.5.2.csv", "pandas", "1.5.2", date, cursor)
    init_module("knowledge_base/sklearn_2023-1-17_1.2.0.csv", "sklearn", "1.2.0", date, cursor)
    init_rules_from_file(cursor)
    return connection


if __name__ == "__main__":
    connection = sqlite3.connect("knowledge_base.db")
    cursor = connection.cursor()
    init_db(cursor)
    date = datetime.date(2023, 1, 17)
    init_module("knowledge_base/pandas 2023-1-17 1.5.2.csv", "pandas", "1.5.2", date, cursor)
    init_module("knowledge_base/sklearn_2023-1-17_1.2.0.csv", "sklearn", "1.2.0", date, cursor)
    init_rules_from_file(cursor)
    connection.close()
