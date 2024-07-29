import sys, os, warnings, json, xmltodict
from nornir import InitNornir
from nornir.core.task import Task
from nornir_utils.plugins.functions import print_result
from rich import print

warnings.simplefilter("ignore", DeprecationWarning)
script_dir = os.path.dirname(os.path.realpath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'utilities_scripts'))
from utilities_scripts.main_func import main
from utilities_scripts.connection_api import connect_to_device, edit_device_config  

class InterfaceManager:
    def __init__(self, config_file="config.yml"):
        self.nr = InitNornir(config_file=config_file)
        self.target_host = None

    def set_target_host(self, hostname):
        self.target_host = hostname

    def operations(self):
        while True:
            print("\nSpecify Operation.....")
            print("1. Get interfaces")
            print("2. Create interfaces")
            print("3. Update interfaces")
            print("4. Delete interfaces")
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
        non_junos_filter = """
            <interfaces xmlns="http://openconfig.net/yang/interfaces">
                <interface>
                    <name/>
                </interface>
            </interfaces>
            """
        try:
            with connect_to_device(task) as m:  # Use the imported utility function
                print("Connected to the device")
                try:
                    netconf_reply = m.get_config(source="running")
                    data_dict = xmltodict.parse(netconf_reply.xml, dict_constructor=dict)
                    relevant_data = data_dict['rpc-reply']['data']['configuration']["interfaces"]["interface"]
                except:
                    netconf_reply = m.get_config(source="running", filter=("subtree", non_junos_filter))
                    data_dict = xmltodict.parse(netconf_reply.xml, dict_constructor=dict)
                    relevant_data = data_dict['rpc-reply']['data']["interfaces"]["interface"]
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

    def create(self, task: Task, interface_name, interface_type, description):
        interface_config = f"""
        <config>
            <interfaces xmlns="http://openconfig.net/yang/interfaces">
                <interface>
                    <name>{interface_name}</name>
                    <config>
                        <name>{interface_name}</name>
                        <type>{interface_type}</type>
                        <description>{description}</description>
                    </config>
                </interface>
            </interfaces>
        </config>
        """
        try:
            netconf_reply = edit_device_config(task, config=interface_config) 
            print(netconf_reply)
            return "Interface created successfully"
        except Exception as e:
            return str(e)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python vlan_operations.py <target> [key=value ...]")
        sys.exit(1)
    
    target = sys.argv[1]
    kwargs = dict(arg.split('=') for arg in sys.argv[2:])
    main(target, InterfaceManager, **kwargs)
