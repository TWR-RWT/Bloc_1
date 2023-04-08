#! C:\Users\tgp\AppData\Local\Programs\Python\Python310\python.exe
from app import app

if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=int("8080"),
        debug=True
    )
#flask --app app --debug app