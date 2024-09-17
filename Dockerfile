FROM python:3.11
COPY ./dist/satisfactoryprometheusexporter-0.1.0-py3-none-any.whl /tmp/
RUN pip install /tmp/satisfactoryprometheusexporter-0.1.0-py3-none-any.whl
CMD ["flask", "run", "--host=0.0.0.0", "--port=8075"]
EXPOSE 8075