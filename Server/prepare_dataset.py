import os
import shutil
import random
import glob

BASE_PATH = 'D:\\Training Data\\Training Dataset'

# for folder in glob.glob(BASE_PATH + '\\filtered\\all\\*'):
#     if folder.split('\\')[-1] == '30':
#         continue
#     num_files = len(os.listdir(folder))
#
#     training_files = random.sample(glob.glob(folder + "\\*"), int(num_files*0.85))
#     for file in training_files:
#         filename = file.split('\\')[-1]
#         folder_name = folder.split('\\')[-1]
#         shutil.move(file, f'{BASE_PATH}\\training\\{folder_name}\\{filename}')
#
#     validation_files = random.sample(glob.glob(folder + "\\*"), int(num_files*0.10))
#     for file in validation_files:
#         filename = file.split('\\')[-1]
#         folder_name = folder.split('\\')[-1]
#         shutil.move(file, f'{BASE_PATH}\\validation\\{folder_name}\\{filename}')
#
#     test_files = random.sample(glob.glob(folder + "\\*"), int(num_files * 0.05))
#     for file in test_files:
#         filename = file.split('\\')[-1]
#         folder_name = folder.split('\\')[-1]
#         shutil.move(file, f'{BASE_PATH}\\test\\{folder_name}\\{filename}')

#
# for folder in glob.glob('C:\\Users\\USER\\Desktop\\training_merged - Copy\\*'):
#     for file in glob.glob(folder + '\\*'):
#         filename = file.split('\\')[-1]
#         shutil.move(file, f'C:\\Users\\USER\\Desktop\\training_all\\{filename}')

# for folder in glob.glob('D:\\Training Data\\Training Dataset\\non_filtered_train\\*'):
#     num_files = min(len(os.listdir(folder)) - 400, 10400)
#
#     test_files = random.sample(glob.glob(folder + "\\*"), 400)
#     for file in test_files:
#         filename = file.split('\\')[-1]
#         folder_name = folder.split('\\')[-1]
#         shutil.move(file, f'non_filtered_test\\{folder_name}\\{filename}')
#
#     validation_files = random.sample(glob.glob(folder + "\\*"), int(num_files * 0.1))
#     for file in validation_files:
#         filename = file.split('\\')[-1]
#         folder_name = folder.split('\\')[-1]
#         shutil.move(file, f'non_filtered_validation\\{folder_name}\\{filename}')
#
#     training_files = random.sample(glob.glob(folder + "\\*"), int(num_files * 0.9))
#     for file in training_files:
#         filename = file.split('\\')[-1]
#         folder_name = folder.split('\\')[-1]
#         shutil.move(file, f'non_filtered_training_2\\{folder_name}\\{filename}')



