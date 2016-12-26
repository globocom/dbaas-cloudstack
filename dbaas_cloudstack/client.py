# -*- coding: utf-8 -*-
import hashlib
import hmac
import base64
import json
import urllib
import logging


LOG = logging.getLogger(__name__)


class SignedApiCall(object):
    def __init__(self, api_url, apiKey, secret):
        self.api_url = api_url
        self.apiKey = apiKey
        self.secret = secret

    def request(self, args, action):
        args['apiKey'] = self.apiKey

        self.params = []
        self._sort_request(args)
        self._create_signature()
        self._build_post_request(action)

    def _sort_request(self, args):
        keys = sorted(args.keys())

        for key in keys:
            self.params.append(key + '=' + urllib.quote_plus(args[key]))

    def _create_signature(self):
        self.query = '&'.join(self.params)
        digest = hmac.new(
            self.secret,
            msg=self.query.lower(),
            digestmod=hashlib.sha1).digest()

        self.signature = base64.b64encode(digest)

    def _build_post_request(self, action):
        self.query += '&signature=' + urllib.quote_plus(self.signature)
        self.value = self.api_url
        if action == 'GET':
            self.value += '?' + self.query


class CloudStackClient(SignedApiCall):
    def __getattr__(self, name):
        def handlerFunction(*args, **kwargs):
            action = args[0] or 'GET'
            if kwargs:
                return self._make_request(name, kwargs)
            return self._make_request(name, args[1], action)
        return handlerFunction

    def _http_get(self, url):
        response = urllib.urlopen(url)
        return response.read()

    def _http_post(self, url, data):
        response = urllib.urlopen(url, data)
        return response.read()

    def _make_request(self, command, args, action):
        args['response'] = 'json'
        args['command'] = command
        self.request(args, action)
        if action == 'GET':
            data = self._http_get(self.value)
        else:
            data = self._http_post(self.value, self.query)
        # The response is of the format {commandresponse: actual-data}
        key = command.lower() + "response"
        if key == 'addiptonicresponse':
            key = 'addiptovmnicresponse'
        jsondata = json.loads(data)
        LOG.info("JSON data = {}".format(jsondata))
        return jsondata[key]
