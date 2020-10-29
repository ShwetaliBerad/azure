#!/usr/bin/python
#
# Copyright (c) 2020 Shwetali Berad (@ShwetaliBerad)
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = \
    '''
---
module: azure_rm_hostgroup
version_added: '1.1.0'
short_description: Create and Delete Azure Host Group
description:
    - Create or Delete Azure Host Group.
options:
    resource_group:
        description:
            - The name of the resource group.
        required: true
        type: str
    name:
        description:
            - The name of the Azure Host Group.
        required: true
        type: str
    location:
        description:
            - Azure Resource Location.
        required: true
        type: str
    availability_zone:
        description:
            - Azure Availability Zone
        default: None
        type: str
        choices:
            - 1
            - 2
            - 3
            - None
    fault_domain:
        description:
            - Azure Fault Domain Count
        default: 1
        type: str
        choices:
            - 1
            - 2
            - 3
            - 4
            - 5
    state:
        description:
            - Assert the state of the protection item.
            - Use C(present) for Creating Azure Host Group.
            - Use C(absent) for Deleting Azure Host Group.
        default: present
        type: str
        choices:
            - present
            - absent
extends_documentation_fragment:
    - azure.azcollection.azure
    - azure.azcollection.azure_tags
author:
    - Shwetali Berad (@ShwetaliBerad)
'''

EXAMPLES = '''
    - name: Create/Update Azure Host Group
      azure_rm_hostgroup:
        resource_group: 'myResourceGroup'
        name: 'tesHostGroup'
        location: 'westeurope'
        state: 'present'
    - name: Delete Azure Host Group
      azure_rm_hostgroup:
        resource_group: 'myResourceGroup'
        name: 'tesHostGroup'
        location: 'westeurope'
        state: 'absent'
'''

RETURN = '''
response:
    description:
        - The response about the current state of the Host Group.
    returned: always
    type: complex
    contains:
        id:
            description:
                - Resource ID.
            returned: always
            type: str
            sample:  "/subscriptions/xxxxxxx/resourceGroups/resourcegroup_name/ \
            providers/Microsoft.Compute/hostGroups/host_group_name"
        location:
            description:
                - The location of the resource.
            returned: always
            type: str
            sample: "eastus"
        name:
            description:
                - Name of the Host Group name.
            returned: always
            type: str
            sample: revault_name
        properties:
            description:
                - The Host Group properties.
            returned: always
            type: dict
            sample: {
                        "platformFaultDomainCount": 1,
                    }
        Zones:
            description:
                - The availability zone associated to Host Group
            returned: if availability zone is not None
            type: arr
            sample: [
                        "2"
                    ]
'''

from ansible_collections.azure.azcollection.plugins.module_utils.azure_rm_common_rest import GenericRestClient
from ansible_collections.azure.azcollection.plugins.module_utils.azure_rm_common_ext import AzureRMModuleBaseExt
import re
import json
import time

try:
    from msrestazure.azure_exceptions import CloudError
except ImportError:
    # This is handled in azure_rm_common
    pass


class AzureRMHostGroup(AzureRMModuleBaseExt):
    def __init__(self):
        self.module_arg_spec = dict(
            resource_group=dict(
                type='str',
                required=True
            ),
            name=dict(
                type='str',
                required=True
            ),
            location=dict(
                type='str',
                required=True
            ),
            availability_zone=dict(
                type='str',
                default='None',
                choices=['None','1','2','3']
            ),
            fault_domain=dict(
                type='str',
                default='1',
                choices=['1','2','3','4','5']
            ),
            state=dict(
                type='str',
                default='present',
                choices=['present', 'absent']
            )
        )

        self.resource_group = None
        self.name = None
        self.location = None
        self.availability_zone = None
        self.fault_domain = None
        self.state = None

        self.results = dict(changed=False)
        self.mgmt_client = None
        self.url = None
        self.status_code = [200, 201, 202, 204]

        self.body = {}
        self.query_parameters = {}
        self.query_parameters['api-version'] = None
        self.header_parameters = {}
        self.header_parameters['Content-Type'] = 'application/json; charset=utf-8'

        super(AzureRMHostGroup, self).__init__(derived_arg_spec=self.module_arg_spec,
                                                           supports_check_mode=True,
                                                           supports_tags=True
                                                           )

    def get_api_version(self):
        return '2020-06-01'

    def get_url(self):
        if self.state == 'present' or self.state == 'absent':
            return '/subscriptions/' \
                   + self.subscription_id \
                   + '/resourceGroups/' \
                   + self.resource_group \
                   + '/providers/Microsoft.Compute' \
                   + '/hostGroups' + '/' \
                   + self.name

    def get_body(self):
        if self.state == 'present':
            return {
                "properties": {
                    "platformFaultDomainCount": self.fault_domain
                },
                "zones": [
                    self.availability_zone
                ],
                "location": self.location
            }
        else:
            return {}

    def exec_module(self, **kwargs):
        for key in list(self.module_arg_spec.keys()):
            if hasattr(self, key):
                setattr(self, key, kwargs[key])
            elif kwargs[key] is not None:
                self.body[key] = kwargs[key]

        self.inflate_parameters(self.module_arg_spec, self.body, 0)

        self.query_parameters['api-version'] = self.get_api_version()
        self.url = self.get_url()
        self.body = self.get_body()
        old_response = None
        response = None

        self.mgmt_client = self.get_mgmt_svc_client(GenericRestClient,
                                                    base_url=self._cloud_environment.endpoints.resource_manager)

        old_response = self.get_resource()

        changed = False
        if self.state == 'present':
            if old_response is False:
                changed = True
                response = self.create_recovery_service_vault()
            else:
                changed = False
                response = old_response
        if self.state == 'absent':
            changed = True
            response = self.delete_recovery_service_vault()

        self.results['response'] = response
        self.results['changed'] = changed

        return self.results

    def create_recovery_service_vault(self):
        # self.log('Creating Host Group Name {0}'.format(self.))
        try:
            response = self.mgmt_client.query(
                self.url,
                'PUT',
                self.query_parameters,
                self.header_parameters,
                self.body,
                self.status_code,
                600,
                30,
            )
        except CloudError as e:
            self.log('Error in creating Azure Host Group.')
            self.fail('Error in creating Azure Host Group {0}'.format(str(e)))

        try:
            response = json.loads(response.text)
        except Exception:
            response = {'text': response.text}

        return response

    def delete_recovery_service_vault(self):
        # self.log('Deleting Host Group {0}'.format(self.))
        try:
            response = self.mgmt_client.query(
                self.url,
                'DELETE',
                self.query_parameters,
                self.header_parameters,
                None,
                self.status_code,
                600,
                30,
            )
        except CloudError as e:
            self.log('Error attempting to delete Azure Host Group.')
            self.fail('Error while deleting Azure Host Group: {0}'.format(str(e)))

        try:
            response = json.loads(response.text)
        except Exception:
            response = {'text': response.text}
        return response

    def get_resource(self):
        # self.log('Get Host Group Name {0}'.format(self.))
        found = False
        try:
            response = self.mgmt_client.query(
                self.url,
                'GET',
                self.query_parameters,
                self.header_parameters,
                None,
                self.status_code,
                600,
                30,
            )
            found = True
        except CloudError as e:
            self.log('Host Group Does not exist.')
        if found is True:
            response = json.loads(response.text)
            return response
        else:
            return False


def main():
    AzureRMHostGroup()


if __name__ == '__main__':
    main()
