from flask import Flask, render_template, request, flash, redirect
from flask_wtf import FlaskForm

from wtforms import TextField, IntegerField, TextAreaField, SubmitField, RadioField, SelectField
from wtforms import validators, ValidationError
import csv

#Importing libraries for the algorithm
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestRegressor

#answers can be accessed from the answers[] array
#Questions need to be written in the questions.txt file
#corresponding options need to be filled in the tvops.csv file
#change no_of_trait_questions accordingly below
app = Flask(__name__)
answers =[]
questions=[]
traits=[]
no_of_trait_questions=5
final_output_array=[]
app.secret_key = 'development key'

qno=0
all_options=[]

with open('question_sets/tvops.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')

    for row in csv_reader:
        all_options.append(row)


class QuestionForm(FlaskForm):

   Options = RadioField('Options', choices = [('1' ,all_options[qno][0]),('2' ,all_options[qno][1]),('3' ,all_options[qno][2])] )

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
            answers.append(float(form.Options.data))

            qno=qno+1


            form.Options.choices=[('1',all_options[qno][0]),('2' ,all_options[qno][1]),('3',all_options[qno][2])]


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

    print(traits, answers)
    final_output_array= recommendation_algorithm(traits, answers)
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

"""
ALL THE DATA WORK IS BELOW THIS.
FEEL FREE TO ADJUST ACCORDING TO THE WEBSITE REQUIREMENTS
TODO: BETTER VARIABLE NAMES, OPTIMIZATION, INCLUDE ALL DATASETS, REFACTOR CHUNKS OF CODE
"""

NUMBER_OF_PERSONALITY_QUESTIONS = 5
#Let me test for tv dataset first
data = pd.read_csv("data/final_tv.csv", skipinitialspace=True)

#Data preprocessing
data.drop('Unnamed: 0',axis=1,inplace=True)
data.dropna(inplace=True)

#Creating features dataframe
#full_product_name is the name of column to recommend which acts as a primary key to recognize the product
X = data[[x for x in data.columns if x!="full_product_name"]]

#Create the kmeans model
kmeans_model = KMeans(n_clusters=NUMBER_OF_PERSONALITY_QUESTIONS)

#Train
kmeans_model.fit(X)

#Predict on the same data i.e basically make clusters for the dataset
y_kmeans = kmeans_model.predict(X)

#Make centroids
centroid_positions = kmeans_model.cluster_centers_
new_X_centroids = np.zeros((NUMBER_OF_PERSONALITY_QUESTIONS,NUMBER_OF_PERSONALITY_QUESTIONS))
#Setting values randomly for now but has to be evaluated by seeing the products
new_X_centroids[0,0] = 1
new_X_centroids[1,1] = 1
new_X_centroids[2,2] = 1
new_X_centroids[3,3] = 1
new_X_centroids[4,4] = 1

#Calculating P value for centroids
P_centroids = np.zeros((NUMBER_OF_PERSONALITY_QUESTIONS,NUMBER_OF_PERSONALITY_QUESTIONS))
for i in range(len(centroid_positions)):
    disti = []
    for j in range(len(centroid_positions)):
        disti.append(sum(np.sqrt((centroid_positions[i] - centroid_positions[j])**2)))
    disti /= (max(disti)+np.average(disti))
    disti = 1 - disti
    P_centroids[i] = np.array(disti)

#Calculate distance for all the data points to calculate P value
P_dist = np.zeros(len(y_kmeans))
for ind, val in enumerate(y_kmeans):
    d = sum(np.sqrt((centroid_positions[val] - X.iloc[ind].values)**2))
    P_dist[ind] = d

#I am sure there is a better way to do it
def get_indices(arr, x):
    indices = []
    for i in range(len(arr)):
        if arr[i]==x:
            indices.append(i)
    return indices
P_X = np.zeros((len(y_kmeans), NUMBER_OF_PERSONALITY_QUESTIONS))

#Calculate P value for all the data points
#i is the personality
#j is the centroid's personality
for i in range(NUMBER_OF_PERSONALITY_QUESTIONS):
    for j in range(NUMBER_OF_PERSONALITY_QUESTIONS):
        P_X[get_indices(y_kmeans, i), j] = P_centroids[i,j] - (P_centroids[i,j]/max(P_dist[get_indices(y_kmeans, i)]))*P_dist[get_indices(y_kmeans, i)]

#Creating random forest regressor to perform supervised learning
#This will basically generate mapping between the features and personality
rfr_model = RandomForestRegressor(max_depth=30)
rfr_model.fit(P_X, X)

def recommendation_algorithm(personality_answers_array, tech_answers_array):
    # Make sure to return a list/array object or anything else and changes on the @output route accordingly
    predictedX_features = rfr_model.predict([personality_answers_array])

    #This is the rule for deciding on how to transition to feature question set
    #For now I am choosing closest 20 points
    closest = np.argsort(np.sum((X.values - predictedX_features)**2, axis=1))[:20]

    #After getting the predicted feature vector we can rank the things
    predicted_products = []
    closest_for_fx = np.argsort(np.sum((X.values - tech_answers_array)**2, axis=1))[:3]

    #The datatype is the series, FINAL OUTPUT
    recommended_products = data.iloc[closest_for_fx]['full_product_name']

    return recommended_products.to_list()
