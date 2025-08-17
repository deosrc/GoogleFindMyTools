FROM python:3.13.6-slim

WORKDIR /app

# Install requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy app source
COPY . .

ENV MQTT_HOST=
ENV MQTT_USERNAME=
ENV MQTT_PASSWORD=
ENV UPDATE_INTERVAL=120

CMD [ "python", "./mqtt.py" ]
