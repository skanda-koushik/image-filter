import os

def hide_folder(folder_path):
    try:
        # Check if the folder exists
        if not os.path.exists(folder_path):
            raise FileNotFoundError("Folder not found.")
        
        # Hide the folder by setting the 'hidden' attribute
        os.system(f'attrib +h "{folder_path}"')
        print(f"{folder_path} has been hidden.")
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
folder_to_hide = "folder"
hide_folder(folder_to_hide)
