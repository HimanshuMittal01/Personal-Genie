from flask import Flask, render_template, request
import csv


app = Flask(__name__)
answers =[]
questions=[]

@app.route('/tvsearch')
def tvsearch():
    f = open("question_sets/tvset.txt")
    questions=f.readlines()
    f.close()
    return render_template('tvsearch.html', question=questions[0])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/inspire')
def inspire():
    return render_template('inspireme.html')

@app.route('/output')
def output():
	return render_template('output.html')

if __name__ == '__main__':
    app.run(debug=True)

