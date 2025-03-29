import os

def print_folder_structure(folder_path=".", indent=""):
    try:
        items = os.listdir(folder_path)
    except PermissionError:
        print(f"{indent}📂 [Access Denied]")
        return

    for item in items:
        item_path = os.path.join(folder_path, item)
        if os.path.isdir(item_path):
            print(f"{indent}📂 {item}")
            print_folder_structure(item_path, indent + "    ")
        else:
            print(f"{indent}📄 {item}")

if __name__ == "__main__":
    folder_path = input("Enter folder path (default: current): ") or "."
    print_folder_structure(folder_path)
