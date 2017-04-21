import BaseHTTPServer
import jinja2
from jinja2 import TemplateNotFound, Template
import os
import re

rule_pattern = re.compile("([^<]*)<([^>]+)>([^<]*)")
pattern = re.compile("([^<]*)<([^>]+)>")

url_rules = {}
template_folder = 'templates'

session = {}

port = 8100

def url_rule_match_part(url_rule, url):
    matches = pattern.findall(url_rule)

    if len(matches) == 0:
        if url.startswith(url_rule):
            return {}
        else:
            return False
    ret = {}
    offs = 0
    for mi, match in enumerate(matches):
        i = url[offs:].find(match[0])
        if i < 0 or (mi == 0 and i != 0):
            return False
        if mi >= 1:
            ret[matches[mi-1][1]] = url[offs:offs+i]
        offs += i + len(match[0])
    fl = sum((sum([len(i) for i in match]) + 2) for match in matches) # plus length of '<>': 2
    rl = len(url_rule) - fl
    if rl > 0:
        i = url[offs:].find(url_rule[fl:])
        if i < 0 or offs+i+rl != len(url):
            return False
        ret[match[1]] = url[offs:offs+i]
    else:
        ret[match[1]] = url[offs:]
    return ret

def url_rule_match(url_rule, url):
    url_rule_parts = url_rule.strip('/').split('/')
    url_parts = url.strip('/').split('/')
    if len(url_rule_parts) != len(url_parts):
        return False
    matches = {}
    for url_rule_part, url_part in zip(url_rule_parts, url_parts):
        res = url_rule_match_part(url_rule_part, url_part)
        if res == False:
            return False
        matches.update(res)
    return matches

def percent_decode(s):
    d = {
        '!': '%21',
        '#': '%23',
        '$': '%24',
        '&': '%26',
        "'": '%27',
        '(': '%28',
        ')': '%29',
        '*': '%2A',
        '+': '%2B',
        ',': '%2C',
        '/': '%2F',
        ':': '%3A',
        ';': '%3B',
        '=': '%3D',
        '?': '%3F',
        '@': '%40',
        '[': '%5B',
        ']': '%5D',
    }

    for k, v in d.iteritems():
        s = s.replace(v, k)
        s = s.replace(v.lower(), k)
    return s

class Hotpot(object):
    def __init__(self, module):
        self.module = module
        self.config = {}

    def route(self, url, **options):
        def decorator(handler):
            for optname, optval in options.iteritems():
                setattr(handler, optname, optval)
            global url_rules; url_rules[url] = handler
            return handler
        return decorator

    def register_blueprint(self, blueprint, url_prefix=''):
        for url, handler in blueprint.url_rules.iteritems():
            handler.template_folder = blueprint.template_folder
            handler.blueprint_name = blueprint.name
            global url_rules; url_rules[url_prefix + url] = handler

    def run(self):
        class HTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
            def do_response(s):
                def send_resp(response):
                    s.send_response(response.status)
                    print "response.headers is:", response.headers
                    for header in response.headers:
                        print "header is:", header
                        s.send_header(*header)
                    s.end_headers()
                    s.wfile.write(str(response.response))

                for url_rule, endpoint in url_rules.iteritems():
                    arg_dict = url_rule_match(url_rule, s.path)
                    if arg_dict != False:
                        try:
                            try:
                                global template_folder; template_folder = endpoint.template_folder
                            except:
                                pass
                            to_send = endpoint(**arg_dict)
                            send_resp(make_response(to_send))
                        except AbortException as e:
                            send_resp(make_response(e.code))
                        break
                else:
                    s.send_response(404)
                    s.send_header("Content-type", "text/html")
                    s.end_headers()
                    s.wfile.write("404 PAGE NOT FOUND")

            def do_GET(s):
                cookie_str = s.headers.getheader('cookie')
                get_cookies(cookie_str)
                request.method = 'GET'
                s.do_response()

            def do_POST(s):
                cookie_str = s.headers.getheader('cookie')
                get_cookies(cookie_str)
                request.method = 'POST'
                content_length = int(s.headers.getheader('content-length'))
                content_type = s.headers.getheader('content-type')
                print "content_type is:", content_type
                content = s.rfile.read(content_length)
                print "content is:"
                print content

                read_post_body(content_type, content)
                s.do_response()

        self.httpd = BaseHTTPServer.HTTPServer(('localhost', port), HTTPRequestHandler)

        try:
            self.httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        self.httpd.server_close()

    def __call__(self, environ, start_response):
        def send_resp(response):
            if response.status == 200:
                status_str = "200 OK"
            elif response.status == 301:
                status_str = "301 Moved Permanently"
            elif response.status == 404:
                status_str = "404 Not Found"
            start_response(status_str, response.headers)
            return [str(response.response)]

        request.method = environ['REQUEST_METHOD']
        cookie_str = environ['HTTP_COOKIE']
        get_cookies(cookie_str)
        if request.method == 'POST':
            content_type = environ['CONTENT_TYPE']
            content_length = int(environ['CONTENT_LENGTH'])
            input_stream = environ['wsgi.input']
            content = input_stream.read(content_length)
            read_post_body(content_type, content)
        for url_rule, endpoint in url_rules.iteritems():
            arg_dict = url_rule_match(url_rule, environ["REQUEST_URI"])
            if arg_dict != False:
                try:
                    try:
                        global template_folder; template_folder = endpoint.template_folder
                    except:
                        pass
                    to_send = endpoint(**arg_dict)
                    return send_resp(make_response(to_send))
                except AbortException as e:
                    return send_resp(make_response(e.code))
                break
        else:
            start_response('404 Not Found', [("Content-type", "text/html")])
            return ["404 PAGE NOT FOUND"]

def read_post_body(content_type, content):
    if content_type.startswith("multipart/form-data"): # file upload
        boundary = content_type.split(';')[1].split('=')[1]
        content = ''.join(content.split(boundary))
        content_headers, content = content.split('\r\n\r\n')
        content_headers = content_headers.split('\r\n')
        content_disposition = [h for h in content_headers if h.startswith("Content-Disposition")][0]
        content_disposition = content_disposition.split(';')
        filename = [p for p in content_disposition if p.strip().startswith("filename")][0].split('=')[1]
        filename = filename.strip('"')
        request.files['file'] = File(filename, content)
    elif content_type == 'application/x-www-form-urlencoded': # form
        content = content.split('&')
        for c in content:
            name, val = c.split('=')
            val.replace('+', ' ')
            val = percent_decode(val)
            request.form[name] = val
        print "request.form is:", request.form
        print "content is:", content

def get_cookies(cookie_str):
    cookies = cookie_str.split('; ')
    for cookie in cookies:
        print "cookie is:", cookie
        k, v = cookie.split('=', 1)
        request.cookies[k] = v

class Blueprint(object):
    def __init__(self, name, module, template_folder):
        self.name = name
        self.module = module
        self.template_folder = template_folder
        self.url_prefixes = []
        self.url_rules = {}

    def route(self, url, **options):
        def decorator(handler):
            for optname, optval in options.iteritems():
                setattr(handler, optname, optval)
            self.url_rules[url] = handler
            return handler
        return decorator

class File(object):
    def __init__(self, filename, content):
        self.filename = filename
        self.content = content

    def save(self, path):
        f = open(path, 'w+')
        f.write(self.content)
        f.close()

class Request(object):
    def __init__(self, method=None):
        self.method = None
        # self.httpd = None
        self.files = {}
        self.form = {}
        self.cookies = {}
request = Request()

def render_template(path):
    try:
        context = { 'url_for': url_for }
        full_path = os.path.join(template_folder, path)
        pathname = template_folder
        filename = path
        loader = jinja2.FileSystemLoader(pathname)
        environment = jinja2.Environment(loader=loader)
        rendered = environment.get_template(filename).render(context)
        return str(rendered)  # convert unicode to str (python 2 str == bytes)
    except Exception as e:
        print "e is:", e
        return "not found..."

class AbortException(Exception):
    def __init__(self, code):
        self.code = code

def abort(code):
    raise AbortException(code)

def url_for(endpoint, **values):
    for url_rule, ep in url_rules.iteritems():
        try:
            ep_name = ep.blueprint_name + "." + ep.__name__
        except AttributeError:
            ep_name = ep.__name__
        if ep_name == endpoint:
            if len(values) == 0:
                return url_rule
            else:
                url = ""
                matches = pattern.findall(url_rule)
                for match in matches:
                    url += match[0]
                    url += values[match[1]]
                fl = sum((sum([len(i) for i in match]) + 2) for match in matches) # add length of '<>': 2
                url += url_rule[fl:]
                return url
    abort(404)

def redirect(location):
    return make_response((301, [("Location", location)]))

class Response(object):
    def __init__(self, response=None, status=None, headers=None):
        if response == None:
            self.response = ''
        else:
            self.response = response
        if status == None:
            self.status = 200
        else:
            self.status = status
        if headers == None:
            self.headers = []
        else:
            self.headers = headers

    def set_cookie(self, key, value='', *args, **kwargs):
        header_val = "%s=%s" % (key, value)
        for val in args:
            header_val += "; " + val
        for k, v in kwargs.iteritems():
            if k == 'max_age':
                header_val += '; ' + 'Max-Age=' + str(v)
            elif k == 'expires':
                header_val += '; ' + 'Expires=' + v
            elif k == 'domain':
                header_val += '; ' + 'Domain=' + v
            elif k == 'path':
                header_val += '; ' + 'Path=' + v
            elif k == 'same_site':
                header_val += '; ' + 'SameSite=' + v
        self.headers.append(("Set-Cookie", header_val))

def make_response(arg):
    if type(arg) == str:
        return Response(response=arg)
    elif type(arg) == int:
        return Response(status=arg)
    elif type(arg) == list:
        return Response(headers=headers)
    elif type(arg) == Response:
        return arg
    elif type(arg) == tuple:
        response = ''
        status = 200
        headers = []
        for val in arg:
            if type(val) == str: # response
                response = val
            elif type(val) == int:
                status = val
            elif type(val) == list:
                headers = val
        print "[make_response] headers is:", headers
        return Response(response, status, headers)

def escape(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
