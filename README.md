# Ansible Collection
## zedr.simple_netbox_inventory_plugin

This is a simple example of an Ansible Inventory plugin that queries
NetBox for a list of Devices. It is the plugin equivalent of
[this Inventory Script](https://gist.github.com/zedr/6979ab2fc49fe13e752a9896d6195c4d).

## Usage
 - To build the collection: `ansible-galaxy collection build `
 - To install the collection locally: `ansible-galaxy collection install <PATH_TO_BUILT_TAR.GZ>`
 - To read the documentation: `ansible-doc -t inventory zedr.simple_netbox_inventory_plugin.netbox_devices`

The `examples` folder has an example plugin configuration file. Configure it
as appropriate, then 
run the plugin from the command line: `ansible-inventory --list -i examples/netbox_inventory.yml`
