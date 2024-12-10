import os
import sys
from io import BytesIO

from django.core.wsgi import get_wsgi_application

# Set the settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Initialize Django
application = get_wsgi_application()

def handler(request, context):
    # Build WSGI environ
    environ = {
        'REQUEST_METHOD': request.method,
        'PATH_INFO': request.path,
        'QUERY_STRING': request.query_string,
        'CONTENT_TYPE': request.headers.get('content-type', ''),
        'CONTENT_LENGTH': request.headers.get('content-length', ''),
        'wsgi.input': BytesIO(request.body),
        'wsgi.errors': sys.stderr,
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https' if request.headers.get('x-forwarded-proto') == 'https' else 'http',
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
    }

    # Add HTTP headers to environ
    for key, value in request.headers.items():
        key = key.upper().replace('-', '_')
        if key not in environ:
            environ['HTTP_' + key] = value

    # Dictionary to capture response data
    response = {}

    def start_response(status, response_headers, exc_info=None):
        response['status'] = status
        response['headers'] = response_headers

    # Call the WSGI application
    result = application(environ, start_response)
    body = b''.join(result)

    # Build the response object for Vercel
    return {
        'statusCode': int(response['status'].split()[0]),
        'headers': {k: v for k, v in response['headers']},
        'body': body.decode('utf-8'),
    }
