class TvcmiError(Exception):
    def __init__(self, rc=None, msg=None):
        if msg is None:
            msg = "An error occurred {error}".format(error=rc)
        super(TvcmiError, self).__init__(msg)
        self.error_code = rc
        self.message = msg


class CallbackError(TvcmiError):
    def __init__(self, msg):
        super(CallbackError, self).__init__(None, msg=msg)


class TLSError(TvcmiError):
    def __init__(self):
        super(TLSError, self).__init__(None, msg="Error occurred when setting TLS.")


class ConnectionParamError(TvcmiError):
    def __init__(self):
        super(ConnectionParamError, self).__init__(None, msg="Error connecting with the provided connection parameters")


class ConnectionError(TvcmiError):
    def __init__(self, rc):
        super(ConnectionError, self).__init__(
            rc, msg="Error connecting to server: {error}".format(error=rc))


class FileError(TvcmiError):
    def __init__(self, file_path, msg, rc):
        self.message = "Could not access the file at {path}. Exited with {error}".format(path=file_path, error=msg)
        self.error_code = rc

        super(FileError, self).__init__(
            rc, msg=self.message)


class ConfigError(TvcmiError):
    def __init__(self, file_path):
        self.message = "Could not retrive data from {file}".format(file=file_path)

        super(ConfigError, self).__init__(None, self.message)


class InputError(TvcmiError):
    def __init__(self, file_path):
        self.message = "One or more fields are missing in the input at {file}".format(file=file_path)

        super(ConfigError, self).__init__(None, self.message)


class DirectoryError(TvcmiError):
    def __init__(self, dir_path, msg, rc):
        self.message = "Could not create a directory at {path}. Exited with {error}".format(path=dir_path, error=msg)
        self.error_code = rc

        super(DirectoryError, self).__init__(
            rc, msg=self.message)


class KeyGenerationError(TvcmiError, IOError):
    def __init__(self, msg, rc):
        super(KeyGenerationError, self).__init__(
            rc, msg="Could not generate the private key. RSABackand is not implemented. ")


class KeyCertificateError(TvcmiError, IOError):
    def __init__(self, msg, rc):
        super(KeyCertificateError, self).__init__(
            rc, msg="Error writing/reading to/from disk: {error}".format(error=rc))

