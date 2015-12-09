from cgi import parse_qs, escape
            
def wsgi_app(environ, start_response):
    parameters = parse_qs(environ.get('QUERY_STRING', ''))
    imei = escape(parameters['imei'][0])
    lkey = escape(parameters['lkey'][0])
    cpuk = escape(parameters['cpuk'][0])  #  Pi Serial Number
    with open("ils.py", "r") as f:
        ils = f.read()
    
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    response_body = 'Imei: ' + imei + ' lkey: ' + lkey + '\n' + ils
    yield response_body.encode()

if __name__ == '__main__':
    from wsgiref.simple_server import make_server

    httpd = make_server('localhost', 5555, wsgi_app)
    httpd.serve_forever()