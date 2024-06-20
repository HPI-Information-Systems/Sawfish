# Reproducibility Instructions for Discovering Similarity Inclusion Dependencies

The source code and the artifacts required to reproduce the results of the paper “Discovering Similarity Inclusion Dependencies” [1] can be found at the link <https://github.com/HPI-Information-Systems/Sawfish>.

## 1. Prerequisites

First, clone the repository on your machine by running:
`git clone https://github.com/HPI-Information-Systems/Sawfish.git`

The repository uses Git LFS for the datasets. Therefore, ensure that you have installed Git LFS. You can download it [here](https://git-lfs.com/).

Ensure the LFS file has been downloaded correctly by checking the size of `datasets/SawfishDatasets.zip`. It might be necessary to execute `git lfs pull` yourself. You do not need to extract the ZIP file, this will be handled automatically later.
In case there is a rate limit error for LFS, you can download the datasets from [here](https://my.hidrive.com/lnk/K9TA6QHaR). Simply place the zip in the `datasets` directory.

We do not require any special hardware, but we use a main memory threshold of 32GB for the largest dataset. 

## 2. Repository Overview

The structure of the repository is the following:

- The `src/` contains the source code of the Sawfish algorithm, including the algorithm itself (`sawfish/main/java/de/metanome/algorithms/sawfish`) and a Metanome Mock version to test execution (`sawfish/test/java/de/metanome/algorithms/mock`). Additionally, all baselines from the paper are contained.
- The `docker-compose.yml` contains a list of the docker images that are used to execute and test the Sawfish algorithm in different ways.
- The `datasets/` folder includes the four datasets used to reproduce the results in the paper
- The `metanome` folder contains the compiled JAR of the algorithm (created with `mvn clean package`) and a version of the metanome-cli (obtained from the central repository https://github.com/HPI-Information-Systems/Metanome)
- The `plot_generation/` folder includes all scripts to generate the plots output data
- The `paper_generation/` folder includes all scripts to generate the final paper based on the results and generated plots. The paper is then created in `final_paper/`

## 3. Execution

We offer different ways to execute Sawfish, but each one of them requires `docker` and `docker-compose`. If it is not yet installed on your machine, please follow these instructions: <https://docs.docker.com/engine/install/>

Each method differentiates in the ability to customize the output.

<details>
<summary>1. Master Script</summary>

The Master Script is the least customizable, but with one command, the following things will be done:

1. Fetch required input data for Sawfish by unzipping `datasets/SawfishDatasets.zip`
2. Execution of all experiments for the datasets used in the paper (may take up to a week to finish). A single experiment should take at most around two hours. Since the IMDB dataset consistently timed out in ED mode, we excluded those experiments altogether to save time.
3. Generation of all the plots & graphs that can be found in the paper (after execution visible in `paper_generation/figures/` directory)
4. Full compilation of the paper with all new statistics, graphs & plots (after execution visible in `final_paper/paperSINDsKaminsky.pdf`)

The master script can be executed with the .sh file `master-script.sh`.
If you are on MacOS or Linux do the following steps:

1. Make the script executable by running: `chmod +x master-script.sh`
2. Execute `master-script.sh` by running: `sh master-script.sh`

If you are on Windows, do the following steps:

0. Ensure that you are using [Git Bash](https://gitforwindows.org/), [Cygwin](https://www.cygwin.com/) or [Windows Subsystem for Linux (WSL)](https://learn.microsoft.com/en-us/windows/wsl/install).
1. Make the script executable by running:  `chmod +x master-script.sh`
2. Execute `master-script.sh` by running: `./master-script.sh`

</details>

<details>
<summary>2. Run each step separately</summary>

You can also run each step separately, with different docker images.

- To extract the datasets, use `docker-compose up sawfish-datasets-extraction`
- To run all the scripts to generate the results, execute `docker-compose up sawfish-result-generation`
- After generating the results, you can generate the plots seen in the paper with `docker-compose up sawfish-plot-generation`
- To generate the final paper with the new plots, execute `docker-compose up sawfish-paper-generation`

</details>

## 4. Execution Configurations

### Changing parameters

The project contains default values for most configuration options. To run the algorithm, only an input file and the edit distance threshold are required.

Other configuration options are listed below:

- `editDistanceThreshold`: absolute edit distance threshold
- `similarityThreshold`: Jaccard similarity threshold / normalized edit distance threshold
- `tokenMode`: turn on the token mode, which computes the Jaccard similarity instead of the edit distance
- `ignoreShortString`: ignore strings that are shorter than the edit distance threshold, only required for comparison to PassJoin
- `memoryCheckFrequency`: number of values until a memory check occurs
- `maxMemoryUsagePercentage`: percentage of available memory SAWFISH should use
- `writeDataErrors`: creates an output file with the indirect, i.e. non-equal, matches that were found during validation
- `measureTime`: creates an output file with fine-grained time stats
- `ignoreNumericColumns`: ignore columns that only contain numeric values
- `hybridMode`: turns on the hybrid mode of the normalized edit distance computation in SAWFISH
