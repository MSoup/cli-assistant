FROM --platform=arm64 python:3.11.7-bookworm

RUN apt-get update -y && \
    apt-get install -y vim

WORKDIR /

COPY src/* install_scripts/* gpt-cli/install_scripts/
COPY invoke_gpt.sh requirements.txt gpt-cli/

RUN chmod +x gpt-cli/install_scripts/install.sh && \
    chmod +x gpt-cli/invoke_gpt.sh && \
    cd install_scripts && \
    . ./install.sh .bashrc

ENTRYPOINT ["/bin/bash"]