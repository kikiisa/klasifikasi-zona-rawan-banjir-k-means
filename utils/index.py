import os
def check_file_in_dataset_directory(filename):
    dataset_directory = 'dataset'
    file_path = os.path.join(dataset_directory, filename)
    return os.path.isfile(file_path)

