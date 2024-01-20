# SAWFISH

SAWFISH is the first algorithm to efficiently discover similarity inclusion dependencies.

## Setup

1. The code is written using Java 11.
2. Download the available code as a zip file or clone the SAWFISH repository.
3. Install dependencies and build the project with `mvn install`.
4. a) SAWFISH was developed for Metanome. Therefore, the easiest way to try it out is to import it into a running Metanome instance. See the official [webpage](https://metanome.de) on how to set it up.  
b) Alternatively, the project contains a `MetanomeMock` class that can be used to directly run the algorithm.  
c) Lastly, you can make use of the [metanome-cli](https://github.com/sekruse/metanome-cli) if you want a convenient cli interface.

## Configuration
The project contains default values for most configuration options.
To run the algorithm, only an input file and the edit distance threshold are required.

Other configuration options are listed below:

- `editDistanceThreshold`: absolute edit distance threshold
- `similarityThreshold`: normalized edit distance threshold/Jaccard similarity threshold
- `tokenMode`: turn on the token mode, which computes the Jaccard similarity instead of edit distance
- `ignoreShortStrings`: ignore strings that are shorter than the edit distance threshold, only required for comparison to PassJoin
- `memoryCheckFrequency`: number of values until a memory check occurs
- `maxMemoryUsagePercentage`: percentage of available memory SAWFISH should use
- `writeDataErrors`: creates an output file with the indirect matches that were found during validation
- `measureTime`: creates an output file with fine-grained time stats
- `ignoreNumericColumns`: ignore columns that only contain numeric values
- `hybridMode`: turns on the hybrid mode of the normalized edit distance computation in SAWFISH

## Docker Usage

To easily try out the SAWFISH, we provide a dockerfile that contains Metanome and builds SAWFISH.
To build the image, run `docker build -t sawfish .`.
Now, start a container by running `docker run -d -p 8080:8080 -p 8081:8081 sawfish`.
Then, you can access Metanome with SAWFISH installed in your browser at `localhost:8080`.
To try out more datasets, you can mount a directory containing the appropriate csv files to the container like this `docker run -d -p 8080:8080 -p 8081:8081 -v /path/to/your/data:/app/metanome/backend/WEB-INF/classes/inputData/extern sawfish`.
Please note that you might need to change the dataset configuration in Metanome after mounting external csv datasets, since Metanome assumes a certain format.

## Repeatability

The datasets that were used in the publication are available [here](https://hpi.de/naumann/projects/repeatability/data-profiling/metanome-ind-algorithms.html).
To recreate the paper, please follow the instructions provided in [REPRODUCIBILITY_INSTRUCTIONS.md](REPRODUCIBILITY_INSTRUCTIONS.md).

## Joinability Case Study

We have manually annotated all, true sINDs that were discovered by SAWFISH on all relational tables of [this sample](http://data.dws.informatik.uni-mannheim.de/webtables/2015-07/sample.gz) of the 2015 Web Table Corpus. Our annotations are stored in the `joinability_case_study_annotations.csv` with the following schema `[Dependent Table,Dependent Column Index,Referenced Table,Referenced Column Index,Classification]`. The column indices are 0-indexed. The classification distinguishes sINDs into the following classes: `[Meaningful, Coincidental, Erroneous]`.
