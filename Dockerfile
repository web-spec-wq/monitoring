FROM python:3.11-slim
WORKDIR /app
COPY app.py .
RUN mkdir templates
COPY templates/register.html templates/
RUN pip install flask prometheus_client
EXPOSE 5000
CMD [ "python","app.py" ]

