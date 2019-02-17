FROM python:3.5
WORKDIR /home/marcus/git/api/python
# COPY /home/marcus/git/api/docker/door_req.txt ./
RUN pip install flask flask_cors
COPY . .
# https://stackoverflow.com/questions/43925487/how-to-run-gunicorn-on-docker
# CMD ["gunicorn", "-w", "2", "-b", "127.0.0.1:5003", "kong-test:app"]
CMD ["python", "kong-test.py"]

