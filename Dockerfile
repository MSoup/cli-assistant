FROM --platform=arm64 debian:bullseye

RUN apt-get update -y && apt-get install -y vim python3.9 python3-venv

RUN ln -s /usr/bin/python3.9 /usr/bin/python

WORKDIR /

COPY install_scripts/* gpt-cli/install_scripts/
COPY ask.py invoke_gpt.sh requirements.txt gpt-cli/

RUN chmod +x gpt-cli/install_scripts/install.sh && \
    chmod +x gpt-cli/invoke_gpt.sh

ENTRYPOINT ["/bin/bash"]