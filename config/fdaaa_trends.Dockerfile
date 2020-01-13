FROM leandatascience/jupyterlab-ds:latest
ENV MAIN_PATH=/usr/local/bin/fdaaa_trends
ENV LIBS_PATH=${MAIN_PATH}/libs
ENV CONFIG_PATH=${MAIN_PATH}/config
ENV NOTEBOOK_PATH=${MAIN_PATH}/notebooks

COPY requirements.txt /tmp/
RUN pip install --requirement /tmp/requirements.txt

EXPOSE 8888

CMD cd ${MAIN_PATH} && sh config/run_jupyter.sh
