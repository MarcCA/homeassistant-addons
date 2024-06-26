#!/usr/bin/env python3

import sys
import logging
import os
import random
import json
import argparse

sys.path.append('../')

from samsungtvws import SamsungTVWS

# Add command line argument parsing
parser = argparse.ArgumentParser(description='Upload images to Samsung TV.')
parser.add_argument('--upload-all', action='store_true', help='Upload all images at once')
parser.add_argument('--debug', action='store_true', help='Enable debug mode to check if TV is reachable')
parser.add_argument('--tvip', help='IP address of the Samsung the Frame')
parser.add_argument('--picturename', help='Name of the picture to be uploaded and shown')
args = parser.parse_args()

# Increase debug level
logging.basicConfig(level=logging.INFO)
# Set the path to the file that will store the list of uploaded filenames
upload_list_path = '/config/uploaded_temp.json'
upload_file_path = '/config/uploaded_remote_file_temp.json'
upload_media_path = '/config/media_file_temp.json'


def get_picture_arg():
    if len(sys.argv) >= 4:
        picture_arg = sys.argv[4]
        return picture_arg
    else:
        return None  # Handle the case when there are not enough arguments

picture_arg_value = get_picture_arg()
if picture_arg_value:
    print(f"picture argument: {picture_arg_value}")
else:
    print("Not enough arguments provided.")

#sys.exit()

tvip = args.tvip
# Set your TVs local IP address. Highly recommend using a static IP address for your TV.
#tv = SamsungTVWS('192.168.1.146')
tv = SamsungTVWS(tvip)
# Check if TV is reachable in debug mode
# Set the path to the folder containing the images
folder_path = '/media/PCMediaShare'

# Delete last uploaded picture

# get content of file with last upload information

# Delete content of last uploaded file
if os.path.isfile(upload_file_path):
	with open('/config/uploaded_remote_file_temp.json', 'r') as file:
		content = file.read()
		trimmed_content = content.strip('"')
		tv.art().delete(trimmed_content)
		print(str(trimmed_content))
else:
	print(f"Error: {upload_file_path} not found.")


if os.path.isfile(upload_list_path):
    os.remove(upload_list_path)
    print("File removed")
else:
    print(f"Error: {upload_list_path} not found.")

if os.path.isfile(upload_file_path):
    os.remove(upload_file_path)
else:
    print(f"Error: {upload_file_path} not found.")


# Load the list of uploaded filenames from the file
if os.path.isfile(upload_list_path):
		with open(upload_list_path, 'r') as f:
			uploaded_files = json.load(f)
else:
		uploaded_files = []


if args.debug:
		try:
				logging.info('Checking if the TV can be reached.')
				info = tv.rest_device_info()
				logging.info('If you do not see an error, your TV could be reached.')
				sys.exit()
		except Exception as e:
				logging.error('Could not reach the TV: ' + str(e))
				sys.exit()



# Checks if the TV supports art mode
art_mode = tv.art().supported()


if art_mode == True:
		# Retrieve information about the currently selected art
		#current_art = tv.art().get_current()

		# Get a list of JPG/PNG files in the folder, and searches recursively if you want to use subdirectories
		files = [os.path.join(root, f) for root, dirs, files in os.walk(folder_path) for f in files if f.endswith('.jpg') or f.endswith('.png') or f.endswith('.jpeg')]

		#print(str(files))

		if args.upload_all:
				logging.info('Bulk uploading all photos. This may take a while...')

				# Remove the filenames of images that have already been uploaded
				files = list(set(files) - set([f['file'] for f in uploaded_files]))
				files_to_upload = files
		else:
				if len(files) == 0:
						logging.info('No new images to upload.')
				else:
						logging.info('Choosing random image.')
						files_to_upload = [random.choice(files)]
						print(files_to_upload)
						with open("testupload.txt", 'w') as fru:
							fru.write(str(files_to_upload))

		if args.picturename:
				files_to_upload = ["/media/PCMediaShare/" + picture_arg_value]
		else: 
				print("no Picture name given")

		#print(files_to_upload)

		with open("test.txt", 'a+') as fr:
			fr.write(str(files_to_upload))
			fr.write("Section 0")
			
		for file in files_to_upload:
				# Read the contents of the file
				with open(file, 'rb') as f:
						data = f.read()

				with open("test.txt", 'a+') as fr:
					fr.write("Section1")


				# Upload the file to the TV and select it as the current art, or select it using the remote filename if it has already been uploaded
				remote_filename = None
				for uploaded_file in uploaded_files:
						if uploaded_file['file'] == file:
								remote_filename = uploaded_file['remote_filename']
								logging.info('Image already uploaded.')
								with open("test.txt", 'a+') as fr:
									fr.write("Section2")
								break
				if remote_filename is None:
						logging.info('Uploading new image: ' + str(file))

						try:
							if file.endswith('.jpeg') or file.endswith('.jpg'):
									remote_filename = tv.art().upload(data, file_type='JPEG', matte="none")
									with open("test.txt", 'a+') as fr:
										fr.write("Section3")
							elif file.endswith('.png'):
									remote_filename = tv.art().upload(data, file_type='PNG', matte="none")
						except Exception as e:
							logging.error('There was an error: ' + str(e))
							#sys.exit()
							
						# Add the filename to the list of uploaded filenames
						uploaded_files.append({'file': file, 'remote_filename': remote_filename})

						if not args.upload_all:
							# Select the uploaded image using the remote file name
							tv.art().select_image(remote_filename, show=False)
							with open("test.txt", 'a+') as fr:
								fr.write("Section4")

				else:
						if not args.upload_all:
								# Select the image using the remote file name only if not in 'upload-all' mode
								logging.info('Setting existing image, skipping upload')
								#tv.art().select_image(remote_filename, show=True)

				# Save the list of uploaded filenames to the file

				tv.art().select_image(remote_filename, show=True)
				with open("test.txt", 'a+') as fr:
					fr.write("Section6")
				with open(upload_list_path, 'w') as f:
						json.dump(uploaded_files, f)
				with open(upload_file_path, 'w') as f:
						json.dump(remote_filename, f)
else:
		logging.warning('Your TV does not support art mode.')
