import os

project_root = os.getcwd()  # Make sure you're in your project folder
for root, dirs, files in os.walk(project_root):
    for f in files:
        if f.endswith(".html"):
            print(os.path.join(root, f))