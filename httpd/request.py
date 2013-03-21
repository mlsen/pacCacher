import http.server
import httpd.config
import httpd.file
import httpd.log

class RequestHandler(http.server.BaseHTTPRequestHandler):
    """
    The RequestHandler for the HTTP Server.
    Responses with status code 501 (not implemented) if
    - the requested repository doesn't exist
    - the filetype is not allowed for the requested repository.
    If the request is valid it will deliver the file to the remote host
    and save it in the local repository (if it's not in the no_cache list)
    """
    
    def log_message(self, *args):
        # Just to get rid of log messages created by BaseHTTPRequestHandler
        pass

    def do_HEAD(self, valid = True,
                content_type = None,
                content_length = None):

        if valid:
            # Status Code: OK
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', content_length)
        else:
            # Status Code: Not implemented
            self.send_response(501)
        
        self.end_headers()


    def do_GET(self):

        # First extract some information from the path
        file_path = self.path[self.path.find('/', 1):]
        file_name = self.path[self.path.rfind('/'):][1:]
        file_extension = file_name[file_name.rfind('.'):][1:]
        file_repo = self.path[1:self.path.find('/', 1)]

        # Logging
        logger = httpd.log.getLogger(self.client_address[0],
                                     httpd.config.LOG_LEVEL)
        logger.info('Request: {0}'.format(file_name))

        # Check if requested repository exists
        if file_repo not in httpd.config.repo:
            self.do_HEAD(False)
            logger.error('No such repository: {0}'.format(file_repo))
            return
        
        # Get repository configuration
        repo = httpd.config.repo[file_repo]
        
        # Check if file extension is allowed so we don't fetch .ico or sth
        if file_extension not in httpd.config.get_list(
            repo['allowed_filetypes']):
            
            self.do_HEAD(False)
            logger.error('Not serving filetype {0}.'.format(file_extension))
            
        else:
            # True: Don't cache, False: Cache
            no_cache = file_extension in httpd.config.get_list(repo['no_cache'])
            
            try:
                reader, writer, file_size = httpd.file.get(
                    repo.get('local_repo'),
                    repo.get('remote_repo'),
                    file_path, logger, no_cache)
                
            except Exception:
                return

            file_type = 'application/octet-stream'
            self.do_HEAD(True, file_type, file_size)

            if writer:
                # Remote -> save
                httpd.file.write(reader, self.wfile, writer)
            else:
                # Local or Passthrough
                httpd.file.write(reader, self.wfile)
                
            logger.info('{0} delivered!'.format(file_name))
