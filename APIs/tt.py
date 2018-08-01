
try:
    with open("/ee3", 'r') as f:
        print(f)
except FileNotFoundError as e:
    print(e)
    print("tt")
    pass

