FROM python:3.4.2-onbuild
RUN pip install livereload
ENV PORT 8080
CMD python -m colgate_schedule.dev_server
