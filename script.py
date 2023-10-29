from firebase_admin import credentials, firestore, initialize_app
import requests
import json
import math

cred = credentials.Certificate('key.json')
default_app = initialize_app(cred)
db = firestore.client()
collection = db.collection('professors')

def get_num_of_professors(
        id
    ):  # function returns the number of professors in the university of the given ID.
        page = requests.get(
            "http://www.ratemyprofessors.com/filter/professor/?&page=1&filter=teacherlastname_sort_s+asc&query=*%3A*&queryoption=TEACHER&queryBy=schoolId&sid="
            + str(id)
        )  # get request for page
        temp_jsonpage = json.loads(page.content)
        num_of_prof = (
            temp_jsonpage["remaining"] + 20
        )  # get the number of professors at William Paterson University
        return num_of_prof
    
def load_db():
    num_profs = get_num_of_professors(1482)
    num_of_pages = math.ceil(num_profs / 20)

    professor_index = 0
    for i in range(1, num_of_pages + 1):  # the loop insert all professor into list
            page = requests.get(
                "http://www.ratemyprofessors.com/filter/professor/?&page="
                + str(i)
                + "&filter=teacherlastname_sort_s+asc&query=*%3A*&queryoption=TEACHER&queryBy=schoolId&sid="
                + str(1482)
            )
            json_response = json.loads(page.content)
            temp_list = json_response["professors"]


            for json_professor in json_response["professors"]:
                first = json_professor['tFname']
                last = json_professor['tLname']
                rating = json_professor['overall_rating']
                
                data = {
                    'first': first,
                    'last': last,
                    'rating': rating
                }
                
                collection.document(f'{first.split()[0]}_{last.split()[-1]}').set(data)
                professor_index += 1                
                
if __name__ == '__main__':
    load_db()