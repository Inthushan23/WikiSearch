from ....utils.loader_utils.load_data import load_text_file, filter_loaded_data
from ..config import WIKI_FILE_PATH

data = load_text_file(WIKI_FILE_PATH)
filtered_data = filter_loaded_data(data)

print("Init Data length = %d" %len(data.split("\n")))
print("Filtered Data length = %d" %len(filtered_data))
print(filtered_data)

