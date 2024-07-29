from ncclient import manager

def connect_to_device(task):
    host = task.host.hostname
    username = task.host.username
    password = task.host.password
    port = task.host.get("port", 830)
    return manager.connect(
        host=host,
        port=port,
        username=username,
        password=password,
        hostkey_verify=False,
        allow_agent=False,
        look_for_keys=False
    )





def edit_device_config(task, config):
    with connect_to_device(task) as m:
        # Edit the configuration
        edit_reply = m.edit_config(target="running", config=config)
        print("Configuration edited. Reply:")
        print(edit_reply)

        # Validate the configuration
        validate_reply = m.validate(source="running")
        print("Configuration validated. Reply:")
        print(validate_reply)

        # Ask user if they want to commit the changes
        user_input = input("Do you want to commit these changes? (yes/no): ").strip().lower()
        if user_input == 'yes':
            commit_reply = m.commit()
            print("Configuration committed. Reply:")
            print(commit_reply)
            return "Configuration committed successfully"
        else:
            discard_reply = m.discard_changes()
            print("Configuration changes discarded. Reply:")
            print(discard_reply)
            return "Configuration changes discarded"