FROM python:3.5
RUN pip install flask flask_cors flask_jwt_extended requests gunicorn
COPY . .
# CMD ["gunicorn", "-w", "2", "-b", "127.0.0.1:5003", "kong-test:app"]
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5005", "kong-auth-test:app"]
