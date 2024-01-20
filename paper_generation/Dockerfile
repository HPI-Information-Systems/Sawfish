FROM leplusorg/latex:latest
WORKDIR /usr/src/mytex
COPY ./paper_generation .
# Run pdflatex multiple times, so that it gets the references right
RUN pdflatex paperSINDsKaminsky.tex && \
    biber paperSINDsKaminsky.bcf && \
    pdflatex paperSINDsKaminsky.tex
