#!/usr/bin/env python3

"""
Edited version of the code from the Compute Engine API python tutorials at:
    https://cloud.google.com/compute/docs/tutorials/python-guide

This example script shows how to create and delete an instance pragmatically.

"""

import argparse
import os
import time
from enum import Enum

import googleapiclient.discovery
from six.moves import input


class MODES(Enum):
    NEW = 'new'
    SNAPSHOT = 'snapshot'


# [START list_instances]
def list_instances(compute, project, zone):
    result = compute.instances().list(project=project, zone=zone).execute()
    return result['items'] if 'items' in result else None
# [END list_instances]


# [START create_instance]
def create_instance_from_snapshot(compute, project, zone, name, startup_script='hello_world.sh', snapshot='test-604',
                                  snapshot_project='gce-scripting-experiments'):

    if snapshot_project is None or snapshot_project is None:
        raise ValueError('snapshot_project and snapshot_name required')

    image_response = compute.snapshots().get(project=snapshot_project, snapshot=snapshot).execute()

    source_disk_image = image_response['selfLink']

    # Configure the machine
    machine_type = "zones/%s/machineTypes/n1-standard-1" % zone
    # Hardcoding startup script locations
    startup_script_file = open(
        os.path.join(
            os.path.dirname(__file__), 'startup_scripts/{}'.format(startup_script)), 'r').read()

    config = {
        'name': name,
        'machineType': machine_type,

        # Specify the boot disk and the image to use as a source.
        'disks': [
            {
                'boot': True,
                'autoDelete': True,
                'initializeParams': {
                    'sourceSnapshot': source_disk_image,
                }
            }
        ],

        # Specify a network interface with NAT to access the public
        # internet.
        'networkInterfaces': [{
            'network': 'global/networks/default',
            'accessConfigs': [
                {'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}
            ]
        }],

        # Metadata is readable from the instance and allows you to
        # pass configuration from deployment scripts to instances.
        'metadata': {
            'items': [{
                # Startup script is automatically executed by the
                # instance upon startup.
                'key': 'startup-script',
                'value': startup_script_file
            },
            ]
        }
    }

    return compute.instances().insert(
        project=project,
        zone=zone,
        body=config).execute()
# [END create_instance]


# [START delete_instance]
def delete_instance(compute, project, zone, name):
    return compute.instances().delete(
        project=project,
        zone=zone,
        instance=name).execute()
# [END delete_instance]


# [START wait_for_operation]
def wait_for_operation(compute, project, zone, operation):
    print('Waiting for operation to finish...')
    while True:
        result = compute.zoneOperations().get(
            project=project,
            zone=zone,
            operation=operation).execute()

        if result['status'] == 'DONE':
            print("done.")
            if 'error' in result:
                raise Exception(result['error'])
            return result

        time.sleep(1)
# [END wait_for_operation]


# [START run]
def main(project, zone, instance_name, mode, snapshot_name, snapshot_project, wait=True):
    compute = googleapiclient.discovery.build('compute', 'v1')

    if mode == MODES.NEW.value:
        return

    if mode == MODES.SNAPSHOT.value:
        print('Creating instance.')
        operation = create_instance_from_snapshot(compute, project, zone, instance_name,
                                                  snapshot_project=snapshot_project, snapshot=snapshot_name)
        wait_for_operation(compute, project, zone, operation['name'])

    instances = list_instances(compute, project, zone)

    print('Instances in project %s and zone %s:' % (project, zone))
    for instance in instances:
        print(' - ' + instance['name'])

    print("Instance Created")

    if wait:
        input()

    print('Deleting instance.')

    operation = delete_instance(compute, project, zone, instance_name)
    wait_for_operation(compute, project, zone, operation['name'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('project_id', help='Your Google Cloud project ID.')
    parser.add_argument(
        '--zone',
        default='us-central1-f',
        help='Compute Engine zone to deploy to.')
    parser.add_argument(
        '--name', default='demo-instance', help='New instance name.')
    parser.add_argument('mode', help='Create instance from, a snapshot or from a clean image',
                        choices=[mode.value for mode in MODES])
    parser.add_argument('--snapshot_name', help='Name of the disk snapshot to create the instance from',
                        default='test-604', required=False)
    parser.add_argument('--snapshot_project', help='Google Cloud project ID the snapshot belongs to',
                        default='gce-scripting-experiments', required=False)

    args = parser.parse_args()

    print(args)

    main(project=args.project_id, zone=args.zone, instance_name=args.name, mode=args.mode,
         snapshot_name=args.snapshot_name, snapshot_project=args.snapshot_project)
