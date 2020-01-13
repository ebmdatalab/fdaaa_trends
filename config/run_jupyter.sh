#!/bin/bash

cd ~
mkdir .jupyter

# copy the jupyter configuration into home-directory
cp -r ${CONFIG_PATH}/jupyter_notebook_config.py ~/.jupyter/

cd ${MAIN_PATH}


# edit the python3 kernel, that already imports os,sys and the paths to the app and test
cat > /usr/local/share/jupyter/kernels/python3/kernel.json <<EOKERN
{
    "display_name": "Python 3",
    "language": "python",
    "argv": [
        "python3",
        "-c", "import sys, os; sys.path.insert(0, os.path.dirname(os.environ['LIBS_PATH'])); import libs.nbimport; from IPython.kernel.zmq.kernelapp import main; main()",
        "-f", "{connection_file}"
    ],
    "codemirror_mode": {
        "version": 2,
        "name": "ipython"
    }
}
EOKERN

mkdir notebooks
jupyter lab