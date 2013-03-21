import http.server
import httpd

if __name__ == '__main__':
    
    httpd = http.server.HTTPServer(
        (httpd.config.HOST, httpd.config.PORT),
        httpd.request.RequestHandler)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    
    httpd.server_close()
