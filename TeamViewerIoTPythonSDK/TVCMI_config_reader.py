from .TVCMI_Connection_Parameters import ConnectionParameters
from .TVCMI_error import FileError
import os
import re


param_name = ['MqttHost', 'MqttProvisionPort', 'MqttPort', 'MqttKeepAlive', 'CaFile', 'CertFolder']
param_list = []


class TvcmiConfigParser:

    def __init__(self):
        pass

    @staticmethod
    def parser(file_path):

        file_content = ''
        try:
            with open(file_path, 'rt') as in_file:

                for curr_line in in_file:

                    if "#" in curr_line:
                        curr_line = curr_line.split("#")[0] + "\n"
                    file_content += curr_line

                for param in param_name:
                    pattern = re.compile(r"(\b" + param + r")\s((((\/?\w-*)*)(\.?\w*))|(\w*))")
                    print(param)

                    results = pattern.search(file_content)
                    print(results.group(2))
                    param_list.append(results.group(2))

                connector_params = ConnectionParameters(param_list[5], param_list[2], param_list[1], param_list[0],
                                                        param_list[4], param_list[6], param_list[7])

            return connector_params

        except IOError as e:
            raise FileError(file_path, os.strerror(e.errorcode), e.errorcode)
