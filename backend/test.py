# see the content of requirements.txt file
with open("requirements.txt", "r") as file:
    print(file.read())

with open(".env", "r") as file:
    print(file.read())
