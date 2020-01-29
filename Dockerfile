FROM ebmdatalab/datalab-jupyter:python3.8.1-b61e03bc3e71a620ccd5135ef7ed5bc3db197406

# Set up jupyter environment
ENV MAIN_PATH=/home/app/notebook

# Install pip requirements
COPY requirements.txt /tmp/

# Hack until this is fixed https://github.com/jazzband/pip-tools/issues/823
USER root
RUN chmod 644 /tmp/requirements.txt
USER app

RUN pip install --requirement /tmp/requirements.txt

EXPOSE 8888

# This is a custom ipython kernel that allows us to manipulate
# `sys.path` in a consistent way between normal and pytest-with-nbval
# invocations
COPY config/kernel.json /tmp/kernel_with_custom_path/kernel.json
RUN jupyter kernelspec install /tmp/kernel_with_custom_path/ --user --name="python3"

CMD cd ${MAIN_PATH} && PYTHONPATH=${MAIN_PATH} jupyter lab --config=config/jupyter_notebook_config.py
