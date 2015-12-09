# from cgi import parse_qs, escape

def wsgi_app(environ, start_response):
    # parameters = parse_qs(environ.get('QUERY_STRING', ''))
    # if 'subject' in parameters:
    #     subject = escape(parameters['subject'][0])
    # else:
    #     subject = 'World'
    subject = 'World'
    start_response('200 OK', [('Content-Type', 'text/html')])
    return ['''Hello %(subject)s Hello %(subject)s!''' % {'subject': subject}]

    # status = '200 OK'
    # response_headers = [('Content-type', 'text/plain')]
    # start_response(status, response_headers)
    # response_body = 'Hello World'
    # yield response_body.encode()

if __name__ == '__main__':
    from wsgiref.simple_server import make_server

    httpd = make_server('localhost', 5555, wsgi_app)
    httpd.serve_forever()