# Installation instructions

Tested to be working on Python 3.7.4.

1. Create new Python virtual environment:
	- python -m venv odemsa_venv
2. Activate new Python virtual environment:
	- ON LINUX:
		- source odemsa_venv/bin/activate
	- ON WINDOWS:
		- cd odemsa_venv
		- cd Scripts
		- activate
2. Install nmslib from the included .zip file here: https://drive.google.com/file/d/1f4yTe_Vapy2v0hVZL1Z-mkU1HT3cFJf6/view?usp=sharing
	- Extract the zip file
	- cd nmslib\python_bindings\
	- python setup.py install
3. Run:
	- pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.2.4/en_core_sci_lg-0.2.4.tar.gz
4. Install pip requirements:
	- pip install -r requirements.txt
5. Run the program:
	- python pyConTextNLP_Negation_Detector.py
