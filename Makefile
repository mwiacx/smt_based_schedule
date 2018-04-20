
one_shot:
	python3 one_shot.py
	
clean:
	# python2 version
	# rm *.pyc
	rm -rf __pycache__
	rm param_output/*