# SAWFISH
Developed at the Information Systems Group of the Hasso Plattner Institute.

SAWFISH is the first algorithm to efficiently discover similarity inclusion dependencies.

## Setup

1. The code is written using Java 8.
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
- `ignoreShortStrings`: ignore strings that are shorter than the edit distance threshold, only required for comparison to PassJoin
- `memoryCheckFrequency`: number of values until a memory check occurs
- `maxMemoryUsagePercentage`: percentage of available memory SAWFISH should use
- `writeDataErrors`: creates an output file with the indirect matches that were used during validation
- `measureTime`: creates an output file with fine grained time stats
- `ignoreNumericColumns`: ignore columns that only contain numeric values
- `similarityThreshold`: normalized edit distance threshold
- `hybridMode`: turns on the hybrid mode of the normalized edit distance computation in SAWFISH

## Repeatibility
The datasets that were used in the publication are available [here](https://hpi.de/naumann/projects/repeatability/data-profiling/metanome-ind-algorithms.html).