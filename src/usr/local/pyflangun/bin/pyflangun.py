import textwrap

from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return(textwrap.dedent("""\
        <title>PyFlaNg - AirPuff Sampler</title>
        <body bgcolor='#333333'>
        <h1 style='color:yellow'>
        Welcome to AirPuff!
        </h1>
        <font face="Georgia" color="#fff">
        Wherever you go, there you are!
    """) % ())

if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1')

