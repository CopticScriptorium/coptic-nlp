import sys
import os
PY3 = sys.version_info[0] == 3

script_dir = os.path.dirname(os.path.realpath(__file__)) + os.sep
err_dir = script_dir + "errors" + os.sep
lib = os.path.abspath(script_dir + os.sep + ".." + os.sep + "lib")
sys.path.append(lib)

import binder
print(dir(binder))
run_eval = binder.run_eval

if __name__ == "__main__":
	binder.main()
