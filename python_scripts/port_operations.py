import sys,os,warnings,json,xmltodict
from nornir import InitNornir
from nornir.core.task import Task
from nornir_utils.plugins.functions import print_result
from ncclient import manager
from rich import print

# Suppress deprecated warnings
warnings.simplefilter("ignore", DeprecationWarning)

script_dir = os.path.dirname(os.path.realpath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'utilities_scripts'))

from utilities_scripts.vlan_config import generate_vlan_config
from utilities_scripts.main_func import main

class InterfaceManager:
    def __init__(self, config_file="config.yml"):
        self.nr = InitNornir(config_file=config_file)

    def operations(self):
        while True:
            print("\nSpecify Operation.....")
            print("1. Get vlans")
            print("2. Create vlans")
            print("3. Update vlans")
            print("4. Delete vlans")
            operation = input("Enter your choice (1-4): ")
            if operation == "1":
                return "get"
            elif operation == "2":
                return "create"
            elif operation == "3":
                return "update"
            elif operation == "4":
                return "delete"
            else:
                print("Invalid choice. Please specify a valid operation.")
                continue

    def get(self, task: Task, is_dict=False, interactive=True):
        host = task.host.hostname
        username = task.host.username
        password = task.host.password
        port = task.host.get("port", 830)

        filter = """
        <network-instances xmlns="http://openconfig.net/yang/network-instance">
            <network-instance>
                <name>default</name>
                <vlans>
                    <vlan>
                        <vlan-id/>
                    </vlan>
                </vlans>
            </network-instance>
        </network-instances>
        """
        try:
            with manager.connect(
                host=host,
                port=port,
                username=username,
                password=password,
                hostkey_verify=False,
                allow_agent=False,
                look_for_keys=False
            ) as m:
                print("Connected to the device")
                netconf_reply = m.get_config(source="running", filter=("subtree", filter))
                data_dict = xmltodict.parse(netconf_reply.xml, dict_constructor=dict)
                relevant_data = data_dict['rpc-reply']['data']['network-instances']['network-instance']

                if interactive:
                    pretty_json = json.dumps(relevant_data, indent=4)
                    print(pretty_json)
                    return None
                else:
                    if is_dict:
                        return relevant_data
                    else:
                        pretty_json = json.dumps(relevant_data, indent=4)
                        return pretty_json
        except Exception as e:
            return str(e)

    def create(self, task: Task, **kwargs):
        try:
            vlan_data = self.get(task, is_dict=True, interactive=False)
            return generate_vlan_config(vlan_data)
        except Exception as e:
            return f"An error occurred: {str(e)}"

    def update(self, task: Task, **kwargs):
        return "Update operation is not implemented yet."

    def delete(self, task: Task, **kwargs):
        return "Delete operation is not implemented yet."

    def set_output_format(self, format_choice: str):
        if format_choice not in ["json", "xml", "dict"]:
            raise ValueError("Invalid format choice. Please select 'json', 'xml', or 'dict'.")
        self.output_format = format_choice

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python vlan_operations.py <target> [key=value ...]")
        sys.exit(1)
    
    target = sys.argv[1]
    kwargs = dict(arg.split('=') for arg in sys.argv[2:])
    main(target, InterfaceManager, **kwargs)
