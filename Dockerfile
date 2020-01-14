FROM ebmdatalab/datalab-jupyter:python3.8.1

# Set up jupyter environment
ENV MAIN_PATH=/home/app/notebook

# Install pip requirements
COPY requirements.txt /tmp/
RUN pip install --requirement /tmp/requirements.txt

EXPOSE 8888

CMD cd ${MAIN_PATH} && PYTHONPATH=${MAIN_PATH} jupyter lab --config=config/jupyter_notebook_config.py
