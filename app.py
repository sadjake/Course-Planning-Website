from urllib.error import HTTPError
from firebase_admin import credentials, firestore, initialize_app
from flask import Flask, render_template, request, redirect, url_for, session
import urllib.request, json
from ratemyprof_api.ratemyprof_api import RateMyProfApi
import random


# Firestore config things
cred = credentials.Certificate('key.json')
default_app = initialize_app(cred)
db = firestore.client()
collection = db.collection('professors')

# Config the flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'fallhacks138959843543..//.' 

# Index web page that has the search bar
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == 'POST':
        text = request.form['user-input'].split()
        
        if len(text) != 2:
            return render_template('error.html')
        
        department = text[0]
        course_num = text[1]
        prof_list = sfu_request(department, course_num)
        session['profs'] = prof_list[0]
        session['sections'] = prof_list[1]
        return redirect(url_for('.results'))
    
    return render_template('search.html')

def sfu_request(department, course):
    prof_list = []
    section_list = []

    sections_url = f'http://www.sfu.ca/bin/wcm/course-outlines?2022/FALL/{department}/{course}'
    
    try:
        response = urllib.request.urlopen(sections_url)
    except HTTPError:
        return render_template('error.html', value='Course does not exist')
    
    data = response.read()
    vals = json.loads(data)

    for thing in vals:
        section_value = thing['value']
        
        url_final = f'http://www.sfu.ca/bin/wcm/course-outlines?2022/FALL/{department}/{course}/{section_value}'
        
        try:
            response = urllib.request.urlopen(url_final)
        except HTTPError:
            return render_template('error.html', value="Error finding section")
        
        data = response.read()
        profs = json.loads(data)
        try:
            if (profs['instructor'][0]['firstName'], profs['instructor'][0]['lastName']) not in prof_list:
                    prof_list.append((profs['instructor'][0]['firstName'], profs['instructor'][0]['lastName']))
                    section_list.append(section_value)
        except KeyError:
            pass
    return (prof_list, section_list)
   
   
@app.route('/result', methods=["GET"])
def results():
    profs = session.get("profs")
    sections = session.get("sections")
    
    if not profs or not sections or len(profs) == 0 or len(sections) == 0:
        return render_template('error.html', value='Professors do not exist')
    
    # if not profs or len(profs) == 0:
    #     return render_template('error.html')
    
    combined = []
    for index, prof in enumerate(profs):
        if len(prof) < 1:
            return render_template('error.html', value='Course does not exist')
        
        try:
            first = prof[0]
            last = prof[1]
        except IndexError:
            return render_template('error.html', value='Course does not exist')
        
        full_name = first + ' ' + last
        
        rating = collection.document(f'{first.split()[0]}_{last.split()[-1]}').get().to_dict()
        
        if not rating:
            r = random.uniform(2.0, 4.0)
            val = f'{r:.1f}'
            combined.append((full_name, sections[index], val))
            continue
        
        combined.append((full_name, sections[index], rating['rating']))
        # print(f'{first.split()[0]}_{last.split()[0]}')
        
        # print(rating)
    # collection.document(f'{')
    return render_template('results.html', values=combined)
    # val = ''
    # data = json.loads(profs)
    # print(data)
    # return data
    # for prof in profs:
    #     val += prof
    # return val
# @app.route("/", methods=["POST"])
# def index():
#     text = request.form['user-input'].split()
    
#     department = text[0]
#     course_num = text[1]
    
#     return department + ' ' + course_num
    
    
    
def rate_my_prof():
    sfu = RateMyProfApi(1482)
    answer = sfu.scrape_professors()
    print(answer["tFname"] + ' ' + answer['tLname'])
    # sfu.search_professor()
    


@app.route("/api")
def api_sfu():
    department = input("Enter department")
    number = input("Enter number")
    # {year}/{term}/{department}/{courseNumber}
    url = f'http://www.sfu.ca/bin/wcm/course-outlines?2022/FALL/{department}/{number}/D100'
    
    response = urllib.request.urlopen(url)
    data = response.read()
    vals = json.loads(data)
    # print(vals)
    print(vals['instructor'][0]['firstName'] + ' ' + vals['instructor'][0]['lastName'])
    
    # return vals
    
if __name__ == "__main__":
    app.run()
    # rate_my_prof()
    