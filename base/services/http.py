import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def unsafe_get(url, **kwargs):
    return requests.get(url, verify=False, **kwargs)

def unsafe_post(url, **kwargs):
    return requests.post(url, verify=False, **kwargs)

def unsafe_delete(url, **kwargs):
    return requests.delete(url, verify=False, **kwargs)