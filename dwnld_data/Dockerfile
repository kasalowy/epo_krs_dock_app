FROM python:3.11-alpine

ARG SYSTEM_USER_NAME
ARG WORK_DIR

ENV WORK_DIR=${WORK_DIR}

# RUN addgroup -S ${SYSTEM_USER_NAME} && adduser -S ${SYSTEM_USER_NAME} -G ${SYSTEM_USER_NAME}

WORKDIR ${WORK_DIR}
USER ${SYSTEM_USER_NAME}

COPY --chown=${SYSTEM_USER_NAME}:${SYSTEM_USER_NAME} . ${WORK_DIR}

RUN python3 -m pip install -r "${WORK_DIR}/requirements.txt"

CMD ["sh", "-c", "python3 ${WORK_DIR}/main.py"]
# CMD ["tail", "-f", "/dev/null"]