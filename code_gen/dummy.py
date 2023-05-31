import sys

print("Process was here!")
sys.stdout.write("Script stdout 1")

with open("./code_gen/dummy2.py", 'w') as f:
    f.write("print('Hello')")