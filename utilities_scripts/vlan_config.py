def generate_vlan_config(vlan_data):
    vlans = vlan_data['rpc-reply']['data']['network-instances']['network-instance']['vlans']['vlan']
    vlan_ids = [vlan['vlan-id'] for vlan in vlans]
    print(vlan_ids)


def update_vlan_config():
    pass


def delete_vlan_config():
    pass