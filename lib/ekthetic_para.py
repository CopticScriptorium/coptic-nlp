

def ekthetic_to_para(text,sep="<trans"):
	out_units = []
	units = text.split(sep)
	for i, unit in enumerate(units):
		if i == 0:
			out_units.append(unit)
		else:
			unit = sep + unit
			if "ekthetic" in unit:
				unit = '<p p="p"/>' + unit
			elif i == 1:  # Leading para
				unit = '<p p="p"/>' + unit
			out_units.append(unit)
	return "".join(out_units)
