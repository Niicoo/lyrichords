FROM continuumio/miniconda3

# Copy the conda environment file to the container
COPY environment.yaml /

# Create a new Conda environment
RUN conda env create -f /environment.yaml && conda clean -afy

# Activate the Conda environment
ENV PATH /opt/conda/envs/lyrichords_env/bin:$PATH

# Copy the rest of the project files into the container
COPY . /app

# Set the working directory
WORKDIR /app

# Start the application
ENTRYPOINT ["python", "LyricsChords.py"]