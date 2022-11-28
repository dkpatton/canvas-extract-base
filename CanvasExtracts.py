# -*- coding: utf-8 -*-
import requests, argparse, json
from datetime import datetime as dt
from CanvasRequestHandler import RequestHandler as new_req

parser = argparse.ArgumentParser()
parser.add_argument('term_code', nargs='*')
args = parser.parse_args()

url = 'https://canvas.university.edu'
gql_url = url + '/api/graphql'
sharepoint_path = '{SharePoint folder path}'
folder_name = '{data folder path}'
data_folder = '\\'.join([sharepoint_path,folder_name,url])
api_key = '{API Key}'
session = [url, api_key]

def get_term(term_code):
    """ Returns the Canvas term ID ('id') and the UCD term code ('term_code').
        Canvas request handler does not get data from GraphQL API, so it's just 
        all managed through this function.
    """
    auth = {'Authorization': 'Bearer ' + api_key}
    if term_code == 'from_now':    
        if dt.now().month < 4:
            q = '01'
        elif dt.now().month < 7:
            q = '03'
        elif dt.now().month < 10:
            q = '08'
        else:
            q = '10'
        y = str(dt.now().year)
        term_code = '{y}{q}'.format(y=y,q=q)
    q = ''' query TermID {
                    term(sisId: "{sisId}") {
                        name
                        sisTermId
                        _id
                    }
                }'''.replace('{sisId}', term_code)
    term_req = requests.post(gql_url, headers=auth, params={'query': q}, data={})       
    return {'id': term_req.json()['data']['term']['_id'], 'term_code': term_code}


if args.term_code:
    term = get_term(args.term_code[0])
else:
    term = get_term()

term_id = term['id']
term_code = term['term_code']

request = new_req(session)  # Instantiate a request handler object
request.set_url('/api/v1/accounts/:account_id/courses', [1])  # Placeholders are replaced in order
request.set_params({'with_enrollments': ['true'], 'published': ['true'],  # Builds the query string
                    'by_subaccounts[]': ['{sa1}', '{sa2}'],'state[]': ['available'],
                    'enrollment_term_id': [str(term['id'])]})

response = request.get()

with open('{file_path}', 'w') as json_file:
    json_file.write(json.dumps(response.json()))
