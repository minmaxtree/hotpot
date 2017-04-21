# def application(environ, start_response):
#     start_response('200 OK', [('Content-Type', 'text/html')])
#     print "environ is:", environ
#     if environ['REQUEST_URI'] == '/':
#         return [b'front page']
#     else:
#         return [b'this page is: ' + environ['REQUEST_URI']]

# class Application:
#     def __init__(self, environ, start_response):
#         self.environ = environ
#         self.start_response = start_response

#     def __iter__(self):
#         self.start_response('200 OK', [('Content-Type', 'text/html')])
#         yield 'Hello!'

class Hotpot(object):
    def __call__(self, environ, start_response):
        self.environ = environ
        self.start_response = start_response
        start_response('200 OK', [('Content-Type', 'text/html')])
        return ['''
<title>Simple Page Blueprint</title>
<div class="page">
    <h1>This is blueprint example</h1>
    <p>
        A simple page blueprint is registered under / and /pages
        you can access it using this URLs:
    </p>
    <ul>
        <li><a href="/hello">/hello</a></li>
        <li><a href="/world">/world</a></li>
    </ul>
    <p>
        Also you can register the same blueprint under another path
    </p>
    <ul>
        <li><a href="/pages/hello">/pages/hello</a></li>
        <li><a href="/pages/world">/pages/world</a></li>
    </ul>

    
    Hello

</div>
        ''']

hotpot = Hotpot()
