class Impresys:

    def __new__(cls):
        print("hello")
        cls
    
    def __init__(self):
        print("init")

    def __str__(self):
        return "ok"

if __name__ == "__main__":
    imp = Impresys()
    print(imp)
