FROM python:3.10.5-slim

WORKDIR /app

# Install LaTeX, CM-Super package, and dvipng for LaTeX rendering in Matplotlib
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    texlive-latex-base \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-latex-extra \
    cm-super \
    dvipng && \
    rm -rf /var/lib/apt/lists/*

COPY /plot_generation ./scripts
COPY /datasets/stats ./datasets/stats
RUN pip install --no-cache-dir -r ./scripts/requirements.txt
COPY /results ./results

RUN  chmod +x /app/scripts/generate_all_plots.sh
CMD ["/app/scripts/generate_all_plots.sh"]
