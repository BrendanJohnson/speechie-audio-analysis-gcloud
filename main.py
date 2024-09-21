import functions_framework
from storage import get_item_from_folder, write_to_bucket
import shutil
from subprocess import PIPE, Popen
import os
from flask import make_response, jsonify

def get_data_from_request(request):
	return request['id'], request['file']

def recognizer(input_path):
	try:
		cmd = f'''python3 recognize.py {input_path}'''
		with Popen(cmd, stdout=PIPE, stderr=None, shell=True) as process:
			output = process.communicate()[0].decode("utf-8")
			print(output)
			return output
	except Exception as e:
		print(e)

def transcoder(input_path, output_path):
    try:
        # cmd = f'''ffmpeg -y -i {input_path} {output_path}'''  # Without intelligent volume normalization
        cmd = f'''ffmpeg-normalize {input_path} -lrt 10.0 -c:a pcm_s16le -ar 16000 -f -o {output_path}''' # With intelligent volume normalization
        p = Popen(cmd.split())
        print('Wait for the process to finished')
        stdout, stderr = p.communicate()
        p_status = p.wait()
        print('Process finished')
        return True

    except Exception as e:
        print(e)

@functions_framework.http
def main(request):
	request_json = request.get_json(silent=True)
	request_args = request.args
	audio_id = 'None'
	file_name = 'None'
	input_file = None
	transcoded_file = f'/tmp/out.wav'

	if request_json and 'id' in request_json:
		audio_id, file_name = get_data_from_request(request_json)
	if request_args and 'id' in request_args:
		audio_id, file_name = get_data_from_request(request_args)

	if file_name[:2] == './': # Read file from local file system
		try:
			print('reading from local filesystem')
			input_file = f'/tmp/' + os.path.basename(file_name)
			shutil.copy(file_name, input_file) # Copy file to temp folder
		except FileNotFoundError: 
			input_file = None
	else: # Read file from cloud bucket
		print('reading from cloud')
		input_file = get_item_from_folder(audio_id, file_name)

	if not input_file:
		return make_response(jsonify({ "audioId": audio_id, "filename": file_name, "error": "Audio could not be found error" }), 400)
	
	if transcoder(input_file, transcoded_file):
		print('time to recognize: ' + transcoded_file)
		transcript = recognizer(transcoded_file)
		print('transcribed')
		print(transcript)
		
		write_to_bucket(audio_id, file_name, transcript)
		print('written to bucket')	
		return make_response(jsonify({ "audioId": audio_id, "filename": file_name, "transcript": transcript }), 200)

	return str(input_file)