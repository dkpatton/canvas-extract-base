# -*- coding: utf-8 -*-
from time import sleep
from math import factorial
import requests

class RequestHandler:
    def __init__(self, session):
        self.url = session[0]
        self.auth = {'Authorization': 'Bearer ' + session[1]}
        self.params = ''
        self.data = {}
        self.std_rest = 0
        self.per_page = 25
        self.rate_limit = 700.0
        self.throttle_count = 0

    def set_url(self, doc_endpoint: str, replacements: list=[]):
        """ Expects the endpoint format from the API reference (:id_number).
            Replacements are made in order, for example:
                '/api/v1/accounts/:account_id/courses/:course_id', [1, 123]
                results in 'https://canvas.univ.edu/api/v1/accounts/1/courses/123'
            
            API Reference: https://canvas.instructure.com/doc/api/index.html
        """
        self.endpoint = ''
        doc_endpoint = doc_endpoint.split('/')
        for part in doc_endpoint:
            self.endpoint += '/'
            if part.find(':') >= 0:
                self.endpoint += str(replacements.pop(0))
            else:
                self.endpoint += part
        self.url += self.endpoint
        return self.url

    def set_params(self, params: dict):
        """ Dictionaries are used for inputing a list of values, but these are 
            converted into a query string, since dictionaries can't have multiple 
            keys of the same name.
        """
        query_list = []
        self.params = '?per_page=' + str(self.per_page)
        for param in params:
            for value in params[param]:
                query_list.append('{p}={v}'.format(p=param, v=str(value)))    
        if params:
            self.params += '&'.join(query_list)
        return self.params

    def get(self):
        """ Gets the first request and then subsequent pages (if present).
        """
        more_pages = False
        url = self.url + self.params
        req = requests.get(url, headers=self.auth)
        if 'next' not in req.links.keys():
            return [req.json()]
        else:
            more_pages = True
            pages = [req.json()]
        while more_pages:
            self.throttle(req.headers['X-Rate-Limit-Remaining'])
            req = requests.get(req.links['next']['url'], headers=self.auth)
            pages.append(req.json())
            if 'next' not in req.links.keys():
                return pages
            else:
                pass
    
    def throttle(self, rate_limit_remaining):
        """ For pagingated responses, each time the remaining rate limit drops, 
            a counter is iterated. Each iteration will will force the script to 
            sleep for an exponentially long period (n factorial). On the 7th
            throttle event, an exception is thrown and the script terminates.
        """
        if self.throttle_count > 6:
            raise Exception('Too much throttling. Program ended.')
        if float(rate_limit_remaining) < self.rate_limit:
            self.throttle_count += 1
            sleep(factorial(self.throttle_count))