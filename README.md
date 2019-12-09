# Installation instructions

1. Install nmslib from the included .zip file here: https://drive.google.com/file/d/1f4yTe_Vapy2v0hVZL1Z-mkU1HT3cFJf6/view?usp=sharing
	 - Extract the zip file
	 - cd nmslib\python_bindings\
	 - python setup.py install
 2. Create and activate new Python virtual environment:
	 - python -m venv odemsa_venv
	 - ON LINUX:
		 - source odemsa_venv/bin/activate
	 - ON WINDOWS:
		 - cd odemsa_venv
		 - cd Scripts
		 - activate
 3. Install pip requirements:
	 - pip install -r requirements.txt
 4. Install SciSpacy model as instructed here: 
	 - https://allenai.github.io/scispacy/
 5. Run the program:
	 - python pyConTextNLP_Negation_Detector.py
