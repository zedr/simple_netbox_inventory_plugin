#!/usr/bin/python

# Copyright: (c) 2020, Rigel Di Scala <rigel@redhat.com>
# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import print_function, unicode_literals

import six
import json

from six.moves.urllib.parse import urlencode, urlparse

if six.PY2:
    from httplib import HTTPSConnection, HTTPConnection
else:
    from http.client import HTTPSConnection, HTTPConnection

from ansible.plugins.inventory import BaseInventoryPlugin

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: netbox_devices

plugin_type: inventory

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
plugin: "zedr.simple_netbox_inventory_plugin.netbox_devices"
netbox_auth_token: "abcdef1234567890"
netbox_host_url: "http://netbox.local"
'''


class Device(object):
    """A NetBox device.

    This class implements the data model of a NetBox Device object that
    can be serialised by this module's `NetBoxInventory`.
    """
    default_ssh_port = 22
    default_ssh_user = 'root'
    api_url = '/api/dcim/devices/'

    def __init__(self, ns):
        """Store the namespace.

        Parameters:
            ns:dict The raw data payload for this NetBox object
        """
        self._ns = ns

    @property
    def name(self):
        """The name of this object.

        This is used as the FQDN of the host in Ansible Tower.

        Returns:
            str
        """
        return self._ns['name']

    @property
    def ip_address(self):
        """The primary IP address of this host.

        Returns:
            str
        """
        return self._ns['primary_ip']['address'].split('/')[0]

    @property
    def hostvars(self):
        """The Host Vars associated with this object.

        These are typically used as Ansible Facts in the execution of a Job.

        Returns:
            Dict[str, str]
        """
        return {
            'ansible_port': self.default_ssh_port,
            'ansible_host': self.ip_address,
            'ansible_user': self.default_ssh_user,
            'netbox_tags': self._ns['tags'],
            'netbox_status': self._ns['status']['value']
        }

    def __getitem__(self, item):
        """Attribute queries on this object are delegated to its namespace."""
        return self._ns[item]


class HttpClient(object):
    """A simple HTTP client that is based on the Python 2's stdlib."""

    def __init__(self, host_url, headers=None):
        """Initialise the object with the host URL and any headers to use.

        Parameters:
            host_url:str the URL of the host, e.g. https://tower.local
            headers:Dict any headers to include in the HTTP requests
        """
        url = urlparse(host_url)
        conn_type = HTTPConnection if url.scheme == 'http' else HTTPSConnection
        self.conn = conn_type(url.netloc)
        self.headers = {} if headers is None else headers

    def get(self, path, params=None):
        """Perform a GET request for a given path on the remote host.

        Parameters:
            path:str The URL path
        Returns:
            Response The response object provided by the library.
        """
        encoded_params = urlencode(params or {})
        self.conn.request('GET', path, encoded_params, self.headers)
        return self.conn.getresponse()


class NetBoxInventory(object):
    """A NetBox inventory for the DCIM Device type"""
    grouping = 'site'
    entity_type = Device

    def __init__(self, host_url, token='', http_client_type=HttpClient):
        """Initialise with the host URL, the API Token, and a given client.

        Parameters:
            host_url:str The URL of the host, e.g. https://tower.local
            token:AnyStr A valid NetBox API token
            http_client:HttpClient This module's http client
        """
        headers = {'Authorization': 'Token ' + token} if token else {}
        self.client = http_client_type(host_url, headers=headers)

    @property
    def entities(self):
        """The entities, i.e. hosts, associated with this inventory.

        Returns:
            Generator[Device, None, None]
        """
        next_path = self.entity_type.api_url
        while next_path:
            response = self.client.get(next_path)
            if response.status == 200:
                data = json.load(response)
                next_path = data.get('next', None)
                for item in data['results']:
                    yield self.entity_type(item)
            else:
                raise Exception(
                    'Got a {} response from: {}'.format(
                        response.status,
                        next_path
                    )
                )

    @property
    def host_data(self):
        """Serialise the objects into an Ansible Tower compatible namespace.

        Objects must implement the following interface:

            class Object:
                @property
                @abstractmethod
                def name(self) -> Text:
                    '''The name of the host, i.e. the FQDN.'''

                @property
                @abstractmethod
                def hostvars(self) -> Dict[str, Dict[str, Dict[str, str]]]:
                    '''The HostVars for this host.'''
        Returns:
            typing.Generator[Tuple, None, None]
        """
        for entity in self.entities:
            yield entity.name, entity.hostvars.items()


class InventoryModule(BaseInventoryPlugin):
    """The Inventory Module for querying NetBox Devices."""
    NAME = 'zedr.simple_netbox_inventory_plugin.netbox_devices'

    def verify_file(self, path):
        return True

    def parse(self, inventory, loader, path, cache=True):
        super(InventoryModule, self).parse(
            inventory,
            loader,
            path,
            cache=cache
        )
        self._read_config_data(path=path)
        self.use_cache = cache
        self.inventory = inventory

        auth_token = self.get_option('netbox_auth_token')
        host_url = self.get_option('netbox_host_url')

        netbox_inventory = NetBoxInventory(host_url, token=auth_token)
        for host, variables in netbox_inventory.host_data:
            self.inventory.add_host(host)
            for name, value in variables:
                self.inventory.set_variable(host, name, value)
