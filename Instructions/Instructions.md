# Reproducibility Instructions for Discovering Similarity Inclusion Dependencies

The source code and the artifacts required to reproduce the results of the paper “Discovering Similarity Inclusion Dependencies” [1] can be found at the link <https://github.com/HPI-Information-Systems/Sawfish>.

## 1. Prerequisites

First, clone the repository on your machine by running:
`git clone https://github.com/HPI-Information-Systems/Sawfish.git`

## 2. Repository Overview

The structure of the repository is the following:

- The `src/` contains the source code of the Sawfish algorithm, including the algorithm itself (`sawfish/main/java/de/metanome/algorithms/sawfish`) and the tests (`sawfish/test/java/de/metanome/algorithms/mock`)
- The `docker-compose.yml` contains a list of the docker images that are used to run execute and test the Sawfish algorithm in different ways. 
- The `data_generation/` folder includes all scripts to generate the input data for the testing
- The `plot_and_paper_generation/` folder includes all scripts to generate the plots and the resulting paper from the output data

## 3. Execution

We offerer different ways to execute Sawfish, but each one of them requires docker and docker compose. If it is not yet installed on your machine, please follow these instructions: <https://docs.docker.com/engine/install/>

Each method differentiates in the ability to customize the output.

<details>
<summary>1. Master Script</summary>

The Master Script is the least customizable, but with one command, the following things will be done:

1. Install all needed systems (Maven, Metanome, Python)
2. Fetch all needed input data for Sawfish
3. Execution of the Sawfish Algorithm for all the input data (Can take <span style="color:red">multiple hours</span> to finish)
4. Generation of all the plots & graphs that can be found in the paper (After the execution visible in `paper/graphs/` directory)
5. Full regeneration of the paper with all new statistics, graphs & plots (After the execution visible in `paper/reproduced_paper.pdf`)

The master script can be executed with the command `docker-compose run sawfish-master`.
</details>

<details>
<summary>2. Metanome CLI</summary>
</details>
<details>
<summary>3. Metanome UI</summary>
Metanome is a convenient web platform, that you run locally. It provides a fresh view on data profiling and allows you to execute Sawfish in a more visual way. To use the Metanome UI, follow these instructions:

1. As Sawfish was initially build with the Metanome Web UI, create the main Sawfish image with `docker build -t sawfish .`.
2. Start a container by running `docker run -d -p 8080:8080 -p 8081:8081 sawfish`.
3. Now, open `localhost:8080` in your browser. You should now be able to see Metanome.
4. To get to know how to use Sawfish in Metanome, use the following video as reference:

It is not supported to generate the
<span style="color:red"> Insert Video here <span>
</details>

## 4. Execution Configurations

### Changing parameters

The project contains default values for most configuration options. To run the algorithm, only an input file and the edit distance threshold are required.

Other configuration options are listed below:

- `editDistanceThreshold`: absolute edit distance threshold
- `similarityThreshold`: normalized edit distance threshold/Jaccard similarity threshold
- `tokenMode`: turn on the token mode, which computes the Jaccard similarity instead of edit distance
- `ignoreShortString`: ignore strings that are shorter than the edit distance threshold, only required for comparison to PassJoin
- `memoryCheckFrequency`: number of values until a memory check occurs
- `maxMemoryUsagePercentage`: percentage of available memory SAWFISH should use
- `writeDataErrors`: creates an output file with the indirect matches that were found during validation
- `measureTime`: creates an output file with fine-grained time stats
- `ignoreNumericColumns`: ignore columns that only contain numeric values
- `hybridMode`: turns on the hybrid mode of the normalized edit distance computation in SAWFISH

### Changing the input data

To change the input data, use the Metanome CLI or Metanome UI. add `-v path/to/your/data:/app/metanome/backend/WEB-INF/classes/inputData/extern` to your docker run command. E.g.:
`docker run -d -p 8080:8080 -p 8081:8081 -v /path/to/your/data:/app/metanome/backend/WEB-INF/classes/inputData/extern sawfish`

Remember to replace `path/to/your/data` with your custom path.
