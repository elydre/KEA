import sys

def clear_last_line():
    go_up()
    clear_line()

def go_up():
    sys.stdout.write("\033[F")

def clear_line():
    sys.stdout.write("\033[K")