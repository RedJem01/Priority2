FROM python:latest
WORKDIR /Priority2
COPY . /Priority2
RUN pip3 install -r requirements.txt
ENV FLASK_APP=main
ENV JIRA_TOKEN=''
ENV JIRA_URL=''
ENV JIRA_EMAIL=''
ENV JIRA_PROJECT_KEY=''
ENV ACCESS_KEY=''
ENV SECRET_ACCESS_KEY=''
ENV AWS_REGION=''
ENV P2_QUEUE=''
EXPOSE 8000
CMD ["flask", "run", "--host", "0.0.0.0", "--port", "8000"]