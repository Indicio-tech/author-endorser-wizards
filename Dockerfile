FROM bcgovimages/von-image:py36-1.16-1

WORKDIR /app
COPY ./AuthorWizard.py .
COPY ./EndorserWizard.py .

ENTRYPOINT ["/bin/bash", "-c", "python3 \"$@\"", "--"]
#CMD /app/AuthorWizard.py
