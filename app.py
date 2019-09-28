from flask import Flask, render_template, request, flash, redirect
from flask_wtf import FlaskForm

from wtforms import TextField, IntegerField, TextAreaField, SubmitField, RadioField, SelectField
from wtforms import validators, ValidationError
import csv

#answers can be accessed from the answers[] array
#Questions need to be written in the questions.txt file
#corresponding options need to be filled in the tvops.csv file
#change no_of_trait_questions accordingly below
app = Flask(__name__)
answers =[]
questions=[]
traits=[]
no_of_trait_questions=6
final_output_array=[]
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
    global qno
    
    f = open("question_sets/tvset.txt")
    questions=f.readlines()
    f.close()
    form = QuestionForm()
    
    if request.method == 'POST':
        #Render the same screen when no radio button is selected
        if form.validate() == False:
            return render_template('tvsearch.html', form = form, question=questions[qno])
        
        
        elif(all_questions_answered(questions)):
            
            return redirect('/output')
        

        else:
            #re-initializing the form everytime to update options
            answers.append(form.Options.data)

            qno=qno+1

            form.Options.choices=[('1',all_options[qno][0]),('2',all_options[qno][1]),('3',all_options[qno][2])] 
            return render_template('tvsearch.html', form=form, question=questions[qno])

    elif request.method == 'GET':
        # this part runs for the first question
        return render_template('tvsearch.html', form = form, question=questions[qno] )


    

@app.route('/')
def index():
    clear_all_selections()
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/inspire')
def inspire():
    clear_all_selections()
    return render_template('inspireme.html')

@app.route('/output')
def output():
    global traits
    global answers
    global no_of_trait_questions
    traits=answers[0:no_of_trait_questions]
    del answers[0:no_of_trait_questions]
    
    
    #final_output_array= recommendation_algorithm(answers, traits)
    #For eg= your output is as follows
    final_output_array=['Television 1', 'Televison 2', 'Television 3']
    return render_template('output.html', p1= final_output_array[0], p2=final_output_array[1], p3=final_output_array[2])

@app.route('/recommendation1')
def reccomendation1():
	return render_template('inspireme.html')

@app.route('/home')
def home():
	return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

def all_questions_answered(qarray):
    if(len(qarray)==qno+1):
        return True
    else:
        return False

def clear_all_selections():
    global qno
    qno=0
    global answers
    del answers[:]
    global trait_collection_finished
    trait_collection_finished=False
    global traits
    del traits[:]

def recommendation_algorithm(answers, traits ):
    # Make sure to return a list/array object or anything else and changes on the @output route accordingly
    pass
