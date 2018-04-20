
one_shot:
	python3 one_shot.py

clean:
	# python2 version
	# rm *.pyc
	# rm z3/*.pyc
	rm -rf __pycache__
	rm -rf z3/__pycache__
	rm param_output/*
	rm result/*