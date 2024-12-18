"""
eval.py - controller script wrapping NLP module experiments with sacred for logging

The script reads experiment configurations, one json per line, from `experiments.json`
in the following format:

{"cat":"norm","name":"test_auto_norm","target":"norm_group","train":"silver","test":"ud_test"}
{"cat":"norm","name":"test_auto_norm","target":"norm_group","train":"silver","test":"cyrus"}
{"cat":"tok","name":"test_stacked","target":"norm","train":"silver","test":"ud_test"}

"""
try:
	from sacred import Experiment
	from sacred.observers import MongoObserver
except ImportError:
	pass
from utils.eval_utils import list_files
from six import iteritems
import json, io


ex = Experiment('coptic_nlp')
ex.observers.append(MongoObserver.create())


@ex.config
def my_config():
	params = {}

@ex.main
def run(params):

	ex.add_config({"params":params})

	if "script" not in params:
		raise IOError("No 'script' defined in json configuration:\n" + str(params))

	parse = "pars" in params["script"]
	if "train" in params:
		train_list = list_files(params["train"],parse=parse)
	else:
		train_list = list_files("silver",parse=parse)
	if "test" in params:
		test_list = list_files(params["test"],parse=parse)
	else:
		test_list = list_files("ud_test",parse=parse)

	if "name" not in params:
		raise IOError("No 'name' defined in json configuration:\n" + str(params))
	print("\nRunning task: " + params["name"])
	print("="*80)
	if "norm" in params["script"]:
		from eval_normalization import run_eval
		res = run_eval(train_list,test_list)
	elif "tag" in params["script"]:
		from eval_tagging import run_eval
		tagger = params.get("method","tt")
		retrain = bool(params.get("retrain",False))
		res = run_eval(train_list,test_list,tagger=tagger,retrain=retrain)
	elif "bind" in params["script"]:
		from eval_binding import run_eval
		res = run_eval(train_list,test_list)
	elif "pars" in params["script"]:
		from eval_parsing import run_eval
		retrain = params.get('retrain',False)
		method = params.get('method','malt')
		res = run_eval(train_list,test_list,retrain=retrain,method=method)
	elif "tok" in params["script"]:
		from eval_tokenization import run_eval
		retrain = params.get('retrain',False)
		method = params.get('method','stacked')
		res = run_eval(train_list,test_list,retrain_rf=retrain,method=method)

	if "method" in params:
		ex.log_scalar("method",params["method"])

	for key, value in iteritems(res):
		ex.log_scalar(key,value)

	return res


if __name__ == "__main__":

	experiment_list = io.open("experiments.json").read().strip().split("\n")
	for exp in experiment_list:
		exp = json.loads(exp)

		ex.add_config({"params":exp})
		ex.run_commandline()
		#sys.exit()
