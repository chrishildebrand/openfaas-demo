FROM python:3-alpine

WORKDIR /home/app
#COPY    app.py   .
#COPY    requirements.txt .
COPY    . .

# Add non root user
RUN addgroup -S app && adduser app -S -G app
RUN chown -R app /home/app && mkdir -p /home/app/python && chown -R app /home/app

WORKDIR /home/app
USER app
ENV PATH=$PATH:/home/app/.local/bin:/home/app/python/bin/
ENV PYTHONPATH=$PYTHONPATH:/home/app/python

RUN pip install -r requirements.txt --target=/home/app/python

HEALTHCHECK --interval=3s CMD [ -e /tmp/.lock ] || exit 1

CMD ["python", "app.py"]