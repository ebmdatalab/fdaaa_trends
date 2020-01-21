FROM ebmdatalab/datalab-jupyter:python3.8.1-a0c03278d897c5a5533c564dee5cb8ed9a2f4d12

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

COPY config/kernel.json /tmp/
RUN jupyter kernelspec install /tmp/ --user --name="python3"

CMD cd ${MAIN_PATH} && PYTHONPATH=${MAIN_PATH} jupyter lab --config=config/jupyter_notebook_config.py
