import os
import time

import googleapiclient.discovery


class GCEComputeWrapper(object):

    def __init__(self):
        # Class constants
        self._service_name = 'compute'
        self._service_version = 'v1'
        self._project = 'debian-cloud'
        self._os_name = 'debian-9'

    def _get_gce_resource(self):
        return googleapiclient.discovery.build(self._service_name, self._service_version)

    def get_compute_instance(self):
        compute_res = self._get_gce_resource()
        image_response = compute_res.images().getFromFamily(project=self._project, family=self._os_name).execute()

