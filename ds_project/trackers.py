import io
import sqlite3
from typing import TextIO, Dict
from io import TextIOWrapper

import matplotlib.pyplot as plt
from matplotlib import pyplot

line_counter:Dict[TextIO, int] = {}

def output_tracker(input, stream, run_id):
    if stream in line_counter:
        line_counter[stream] += 1
    else:
        line_counter[stream] = 0
    count = line_counter[stream]

    if isinstance(stream, io.IOBase):
        name = stream.name
    else:
        name = "stdout"
    con = sqlite3.connect("trackers.db")
    cur = con.cursor()
    cur.execute("""INSERT INTO  Outputs VALUES(?, ?, ?, ?)""", (run_id, name, count, str(input)))
    con.commit()

def stdout_tracker(input, run_id: int) -> str:
    output_tracker(input, "stdout", run_id)
    return str(input)

def file_tracker(input: str, file: TextIO, run_id: int) -> str:
    output_tracker(input, file, run_id)
    return input


def plot_tracker(graph_file: str, run_id: int) -> str:
    #plt.savefig("tmp/graph.png")
    f = open(graph_file, "rb")
    bytes = bytearray(f.read())
    con = sqlite3.connect("trackers.db")
    cur = con.cursor()
    cur.execute("""INSERT INTO Plots VALUES(?, ?, ?)""", (run_id, graph_file, bytes))
    con.commit()
    return graph_file

def hyperparam_tracker(function_name: str, hyperparameter:str, value, run_id: int, expr_id : int):
    string_value = str(value)
    con = sqlite3.connect("trackers.db")
    cur = con.cursor()
    cur.execute("""SELECT COALESCE(MAX(times), -1)+1 FROM Hyperparameters WHERE name = ? AND expr_id = ? AND run_id = ?""", (hyperparameter, expr_id, run_id))
    times = cur.fetchone()[0]
    cur.execute("""INSERT INTO Hyperparameters VALUES(?, ?, ?, ?, ?)""", (hyperparameter, string_value, expr_id, times, run_id))
    con.commit()
    return value


if __name__ == "__main__":
    #stdout_tracker([1, "df", 2.4])

    plt.savefig("graphs/something.png")
    plt.savefig(plot_tracker("graphs/something.png", run_id=1))

    some_function_call("abc", 1, True)



    f = open("testfile.txt", "w")

    f.write("sdfoikhjfsdnlkä\n")
    f.write(file_tracker("sdfoikhjfsdnlkä\n", f, run_id=1))


    someHyperparameter = 1
    gaussian_blur(b=0.5, a=someHyperparameter)
    gaussian_blur(b=hyperparam_tracker("gaussian_blur", "b", 0.5, run_id=1, expr_id=1234), a=hyperparam_tracker("gaussian_blur","a", someHyperparameter,run_id = 1))

    # f.write(file_tracker("oisdfgäoihasdf\n", f))
    while someCondition():
        f.write(file_tracker(str(i) + "\n", f, 1))
    f.close()
