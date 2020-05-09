import kaspy

while True:
	text = input('kaspy > ')
	result, error = kaspy.run(text)

	if error: print(error.as_string())
	else: print(result)
