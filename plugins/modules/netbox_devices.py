#!/usr/bin/python

# Copyright: (c) 2020, Rigel Di Scala <rigel@redhat.com>
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: netbox_devices

short_description: An example inventory module for NetBox for querying devices

version_added: "2.4"

description:
    - "This is a simple NetBox Inventory module create for"
    - " demonstration purposes only. It queries a NetBox server in order to"
    - " fetch a list of devices."

options:
    netbox_host_url:
        description:
            - The host URL for the NetBox server, e.g. https://netbox.local
        required: true
    netbox_auth_token:
        description:
            - A authentication token to use for the NetBox server
        required: false

author:
    - Rigel Di Scala <rigel@redhat.com>
'''

EXAMPLES = '''
# Query all Devices local NetBox server using the given authentication token
- name: 
  zedr.simple_netbox_inventory_plugin.netbox_devices:
    name: hello world

'''

from ansible.plugins.inventory import BaseInventoryPlugin


class InventoryModule(BaseInventoryPlugin):
    """The Inventory Module for querying NetBox Devices."""
    NAME = 'netbox_devices'

    def verify_file(self, path):
        return True

    def parse(self, inventory, loader, path, cache=True):
        super(InventoryModule, self).parse(
            inventory,
            loader,
            path,
            cache=cache
        )
        self.use_cache = cache
        self.inventory = inventory
