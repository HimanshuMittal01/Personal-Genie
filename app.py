from flask import Flask, render_template, request, flash
from flask_wtf import FlaskForm

from wtforms import TextField, IntegerField, TextAreaField, SubmitField, RadioField, SelectField
from wtforms import validators, ValidationError
import csv

#answers can be accessed from the answers[] array
#Questions need to be written in the questions.txt file
#corresponding options need to be filled in the tvops.csv file

app = Flask(__name__)
answers =[]
questions=[]
app.secret_key = 'development key'

qno=0
all_options=[]

with open('question_sets/tvops.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    
    for row in csv_reader:
        all_options.append(row)
    

class QuestionForm(FlaskForm):
   
   Options = RadioField('Options', choices = [('1',all_options[qno][0]),('2',all_options[qno][1]),('3',all_options[qno][2])] )

   submit = SubmitField("Send")


@app.route('/tvsearch', methods=['GET','POST'])
def tvsearch():
    f = open("question_sets/tvset.txt")
    questions=f.readlines()
    f.close()
    form = QuestionForm()
    global qno
    if request.method == 'POST':
        #Render the same screen when no radio button is selected
        if form.validate() == False:
            return render_template('tvsearch.html', form = form, question=questions[qno])
        else:
            #re-initializing the form everytime to update options
            qno=qno+1
            answers.append(form.Options.data)
            print(answers)
            form.Options.choices=[('1',all_options[qno][0]),('2',all_options[qno][1]),('3',all_options[qno][2])] 
            return render_template('tvsearch.html', form=form, question=questions[qno])

    elif request.method == 'GET':
        # this part runs for the first question
        return render_template('tvsearch.html', form = form, question=questions[qno] )


    

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/inspire')
def inspire():
    return render_template('inspireme.html')

@app.route('/output')
def output():
	return render_template('output.html')

@app.route('/recommendation1')
def reccomendation1():
	return render_template('inspireme.html')

@app.route('/home')
def home():
	return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
