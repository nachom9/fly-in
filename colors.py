
class PrintColors:

    def print_red(s):
        print("\033[91m{}\033[00m".format(s), end=' ')


    def print_green(s):
        print("\033[92m{}\033[00m".format(s), end=' ')


    def print_yellow(s):
        print("\033[93m{}\033[00m".format(s), end=' ')
