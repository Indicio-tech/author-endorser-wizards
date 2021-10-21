FROM bcgovimages/von-image:py36-1.16-1

WORKDIR /app
COPY ./author/author.py .
COPY ./endorser/EndorserWizard.py .

ENTRYPOINT ["/bin/bash", "-c", "python3 \"$@\"", "--"]
#CMD /app/author.py
