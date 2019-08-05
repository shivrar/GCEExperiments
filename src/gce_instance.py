import os
import time

import googleapiclient.discovery


class GCEComputeInstance(object):

    def __init__(self):
        # Class constants
        self._service_name = 'compute'
        self._service_version = 'v1'

    def get_instance(self):
        return googleapiclient.discovery.build(self._service_name, self._service_version)
