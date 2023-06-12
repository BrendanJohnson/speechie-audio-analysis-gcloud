from allosaurus import app
from argparse import Namespace
# for /REC006_三: 210802_yue_split1_2 > 210809_yue_18_cleanchild
# for /130616_012_三: TOO NOISY
# for /130616_010_三: 210802_yue_split1_2 > 210809_yue_18_cleanchild


config = Namespace(model='210802_yue_split1_2', device_id=-1, lang='yue', approximate=True, prior=None)
model = app.read_recognizer(config)

def recognize_audio(path):
	parameters = { "emit": 1.2, "topk": 3 }
	transcript = model.recognize(path, **parameters)
	return transcript

if __name__ == "__main__":
	transcript = recognize_audio('out.wav')
	print(transcript)