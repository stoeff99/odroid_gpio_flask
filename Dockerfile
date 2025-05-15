FROM ghcr.io/home-assistant/aarch64-base-ubuntu:20.04

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    libffi-dev \
    libcap-dev \
    libgpiod2 \
    python3-libgpiod \
    ca-certificates && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip3 install flask

# Copy your script and s6 run file
COPY gpio_server.py /gpio_server.py
COPY etc/services.d/gpio_server/run /etc/services.d/gpio_server/run
RUN chmod +x /etc/services.d/gpio_server/run


