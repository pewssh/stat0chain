import subprocess

commands = []
for i in range(1,10):
    commands.append(["python3", "main.py", "1", str(i), "10", "5", "40"])

for i in commands:
    subprocess.run(i)
