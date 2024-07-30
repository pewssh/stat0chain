import subprocess

commands = []
for i in range(10,15):
    commands.append(["python3", "main.py", str(i), "1", "10", "5", "40"])

for i in commands:
    subprocess.run(i)
