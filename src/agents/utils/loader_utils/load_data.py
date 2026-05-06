import re


def load_text_file(path: str): # Path to text file
    try:
        file = open(path, "r", encoding="utf-8")
        data = file.read()
        file.close()

    except FileNotFoundError as fnf:
        print(f"Error with the text file...exit - {fnf}")
        return None
    except Exception as e:
        print(f"Error with the text file...exit - {e}")
        return None

    return data


def filter_loaded_data(data: str): # remove none string character
    list_data = data.strip().split("\n")
    rmv_lst = []
    for elt in list_data:
        if not re.match(r'[\w\s-]', elt):
            rmv_lst.append(elt)
    
    return list(set(list_data) - set(rmv_lst))


def load_filtered_text_data(path: str):
    data = load_text_file(path)
    
    if data:
        return filter_loaded_data(data)
    else: 
        return


if __name__ == "__main__":
    data = load_text_file(r"C:\Users\isuthakaran\Dev\explo\mcp-serv\src\agents\tools\wiki_tool\data\wiki_titles")
    print(data)
    