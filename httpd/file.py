import os
import httpd.log
import httpd.config
import urllib.request


def get(local_dir, remote_dir, path, logger, no_cache = False):
    """
    Opens either a local file or an URL.
    local_dir: The local repository
    remote_dir: The remote repository
    path: The relative path of the file to retrieve
    logger: The logger instance

    Returns a tuple in this format:
    (reader, writer, file_size)
    reader and writer are both file objects.
    file_size is the file size in bytes.
    """

    try:
        file_extension = path[path.rfind('.'):][1:]

        # Try to find file locally
        # But first check if its filetype is in the no_cache list
        if no_cache:

            # It is! Go to the remote block by raising FileNotFoundError
            raise FileNotFoundError('.{0} will not be cached.'.format(
                file_extension))
        
        # Check if path exists locally, raises FileNotFoundError if not
        reader, writer, file_size = _get_local(local_dir, path)

    except FileNotFoundError as e:
        
        logger.debug(e)
        # If it doesn't exist locally, fetch it from REPO
        try:
            logger.debug('Trying to fetch: {0}.'.format(
                remote_dir + path))
            reader, writer, file_size = _get_remote(local_dir, remote_dir,
                                                    path, no_cache)
                    
        except urllib.error.HTTPError as e:
            # 404
            logger.warning(e)
            raise

        except OSError as e:
            # Directory could not be created (probably permssions)
            logger.error(e)
            raise

        else:
            # Success -> download
            logger.debug('Found! Downloading.')
                
    else:
        # Success -> local
        logger.debug('{0} found! Serving locally.'.format(local_dir + path))

    return (reader, writer, file_size)


def write(reader, stream_writer, file_writer = None):
    """
    Writes data from the reader to the stream_writer (file object)
    and optionally to the file_writer (if not None)
    """

    # Loop to provide buffering
    while True:

        chunk = reader.read(httpd.config.CHUNK_SIZE)
        if not chunk:
            # EOF
            break

        # Passthrough to client
        stream_writer.write(chunk)
        
        if file_writer:
            # Save locally
            file_writer.write(chunk)

    reader.close()
    if file_writer:
        file_writer.close()


def _get_local(local_dir, path):
    """
    Opens a local file and returns a (reader, writer, file_size) tuple
    where writer is None. (We don't have to write in this case)
    """

    local_path = local_dir + path

    if not os.path.exists(local_path):
        raise FileNotFoundError(local_path + ' doesn\'t exist.')
    
    reader = open(local_path, 'rb')
    file_size = os.path.getsize(local_path)

    # (reader, writer, file_size)
    return (reader, None, file_size)


def _get_remote(local_dir, remote_dir, path, no_cache = False):
    """
    Opens a remote file and returns a (reader, writer, file_size) tuple.
    """
    
    url_path = remote_dir + path
    local_path = local_dir + path

    reader = urllib.request.urlopen(url_path)
    file_size = reader.headers.get('Content-Length')

    # Create directories if they don't exist
    file_dir = local_path[:local_path.rfind('/')]
    if not os.path.exists(file_dir):
        os.makedirs(file_dir, exist_ok=True)

    # Don't open file if no_cache is true        
    if not no_cache:
        writer = open(local_path, 'wb')
    else:
        writer = None

    return (reader, writer, file_size)
