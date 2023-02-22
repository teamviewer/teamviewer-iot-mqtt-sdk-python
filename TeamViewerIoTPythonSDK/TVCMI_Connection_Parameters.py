class ConnectionParameters:
    def __init__(self, directory, client_name, port, port_insecure, host, ca_path, override_certs):
        self.port = port
        self.port_insecure = port_insecure
        self.host = host
        self.ca_path = ca_path
        self.directory = directory
        client_name = client_name.replace(" ","")
        csr_file_name = client_name + "-csr" + ".pem"
        key_der_file_name = client_name + "-key" + ".der"
        cert_der_file_name = client_name + "-cert" + ".der"
        self.key_file_name = client_name + "-key" + ".pem"
        self.cert_file_name = client_name + "-cert" + ".pem"
        self.key_path = directory + "/" + self.key_file_name
        self.cert_path = directory + "/" + self.cert_file_name
        self.csr_path = directory + "/" + csr_file_name
        self.key_der_path = directory + "/" + key_der_file_name
        self.cert_der_path = directory + "/" + cert_der_file_name
        self.ca_der_path = directory + "/ca.der"
        self.override_certs = override_certs
        self.client_name = client_name
        self.csr = None
        self.cert_file = None
        self.key_str = None
        self.user_data = None
