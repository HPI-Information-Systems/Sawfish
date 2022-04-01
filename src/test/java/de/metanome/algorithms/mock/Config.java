package de.metanome.algorithms.mock;

import java.io.File;
import java.util.LinkedList;
import java.util.List;

public class Config {

    public enum Algorithm {
        SAWFISH
    }

    public enum Dataset {
        TPCH, WIKIPEDIA, CENSUS, IMDB
    }

    public Config.Algorithm algorithm;
    public Config.Dataset dataset;

    public List<String> datasetNames = new LinkedList<>();
    public String inputDatasetName;
    public String inputFolderPath = "src" + File.separator + "test" + File.separator + "data" + File.separator;
    public String inputFileEnding = ".csv";
    public String inputFileNullString = "";
    public char inputFileSeparator;
    public char inputFileQuotechar = '\"';
    public char inputFileEscape = '\\';
    public int inputFileSkipLines = 0;
    public boolean inputFileStrictQuotes = false;
    public boolean inputFileIgnoreLeadingWhiteSpace = true;
    public boolean inputFileHasHeader;
    public boolean inputFileSkipDifferingLines = true; // Skip lines that differ from the dataset's schema

    public String measurementsFolderPath = "io" + File.separator + "measurements" + File.separator;

    public String statisticsFileName = "statistics.txt";
    public String resultFileName = "results.txt";

    public boolean writeResults = true;

    public static Config create(String[] args) {
        if (args.length == 0)
            return new Config();


        Config.Algorithm algorithm = null;
        if (args.length >= 2) {
            String algorithmArg = args[1].toLowerCase();
            for (Config.Algorithm possibleAlgorithm : Config.Algorithm.values())
                if (possibleAlgorithm.name().toLowerCase().equals(algorithmArg))
                    algorithm = possibleAlgorithm;
        } else {
            algorithm = Algorithm.SAWFISH;
        }

        Config.Dataset dataset = null;
        String datasetArg = args[0].toLowerCase();
        for (Config.Dataset possibleDataset : Config.Dataset.values())
            if (possibleDataset.name().toLowerCase().equals(datasetArg))
                dataset = possibleDataset;

        if ((algorithm == null) || (dataset == null))
            wrongArguments();

        return new Config(algorithm, dataset);
    }

    private static void wrongArguments() {
        throw new RuntimeException("\nArguments not supported!\nProvide correct values: <algorithm> <dataset>");
    }

    public Config() {
        this(Config.Algorithm.SAWFISH, Dataset.CENSUS);
    }

    public Config(Config.Algorithm algorithm, Config.Dataset dataset) {
        this.algorithm = algorithm;
        this.setDataset(dataset);
    }

    @Override
    public String toString() {
        return "Config:\r\n\t" +
                "algorithm: " + this.algorithm.name() + "\r\n\t" +
                "dataset: " + this.inputDatasetName + this.inputFileEnding;
    }

    private void setDataset(Config.Dataset dataset) {
        this.dataset = dataset;
        if (dataset == Dataset.CENSUS) {
            this.inputDatasetName = "CENSUS/CENSUS";
            this.inputFileSeparator = ';';
            this.inputFileHasHeader = false;
        }
    }
}
