FROM python:2.7


RUN mkdir -p /code/dbaas_cloudstack
WORKDIR /code
RUN apt-get update
RUN apt-get install -y libsasl2-dev python-dev libldap2-dev libssl-dev mysql-client
RUN easy_install ipython==5.1.0 ipdb==0.10.1
RUN git clone https://github.com/globocom/database-as-a-service.git dbaas
RUN pip install -r dbaas/requirements_test.txt
ADD . /code/dbaas_cloudstack
RUN pip install -r dbaas_cloudstack/requirements.txt
RUN cd /code/dbaas_cloudstack; pip install -e .
ENTRYPOINT /code/dbaas_cloudstack/run_tests.sh
