FROM mysql:latest

ARG MYSQL_ROOT_PASSWORD
ARG SYSTEM_USER_NAME
ARG WORK_DIR

USER ${SYSTEM_USER_NAME}
WORKDIR ${WORK_DIR}

ENV MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
ENV SYSTEM_USER_NAME=${SYSTEM_USER_NAME}

COPY --chown=${SYSTEM_USER_NAME}:${SYSTEM_USER_NAME} . ${WORK_DIR}

COPY create_db.sql /docker-entrypoint-initdb.d/
COPY create_tbl_search_results.sql /docker-entrypoint-initdb.d/
COPY load_search_results.sql /docker-entrypoint-initdb.d/

EXPOSE 3306