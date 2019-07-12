class Postprocessor:
	def __init__(self, separator="_"):
		self._sep = separator

	def insert_separators(self, tokens, preds):
		accum = []

		for i, token in enumerate(tokens):
			pred = preds[i]
			accum.append(token.orig)
			if pred == 0:
				accum.append(self._sep)

		return "".join(accum)
