import sys
from rich import print
from nornir_utils.plugins.functions import print_result

def main(target, manager_class, **kwargs):
    config_file = "../config.yml"
    manager = manager_class(config_file=config_file)
    
    operation = manager.operations()
    
    if target in manager.nr.inventory.hosts:
        filtered_nr = manager.nr.filter(name=target)
    else:
        print(f"Target '{target}' not found in inventory.")
        sys.exit(1)

    if operation == "get":
        result = filtered_nr.run(task=manager.get, **kwargs)
    elif operation == "create":
        result = filtered_nr.run(task=manager.create, **kwargs)
    elif operation == "update":
        result = filtered_nr.run(task=manager.update, **kwargs)
    elif operation == "delete":
        result = filtered_nr.run(task=manager.delete, **kwargs)
    else:
        print("Invalid operation specified.")
        sys.exit(1)

    print_result(result)
