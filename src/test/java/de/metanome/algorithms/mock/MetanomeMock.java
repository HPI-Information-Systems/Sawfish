package de.metanome.algorithms.mock;

import de.metanome.algorithm_integration.AlgorithmConfigurationException;
import de.metanome.algorithm_integration.AlgorithmExecutionException;
import de.metanome.algorithm_integration.ColumnIdentifier;
import de.metanome.algorithm_integration.algorithm_types.InclusionDependencyAlgorithm;
import de.metanome.algorithm_integration.configuration.ConfigurationSettingFileInput;
import de.metanome.algorithm_integration.input.InputGenerationException;
import de.metanome.algorithm_integration.input.RelationalInput;
import de.metanome.algorithm_integration.input.RelationalInputGenerator;
import de.metanome.algorithm_integration.results.InclusionDependency;
import de.metanome.algorithm_integration.results.Result;
import de.metanome.algorithms.sawfish.SawfishInterface;
import de.metanome.backend.algorithm_execution.TempFileGenerator;
import de.metanome.backend.input.file.DefaultFileInputGenerator;
import de.metanome.backend.result_receiver.ResultCache;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class MetanomeMock {

    public static void main(String[] args) {
        Config conf = Config.create(args);
        MetanomeMock.execute(conf);
    }

    public static void execute(Config conf) {
        try {
            ArrayList<RelationalInputGenerator> inputGenerators = new ArrayList<>();
            if (conf.datasetNames.isEmpty()) {
                inputGenerators.add(new DefaultFileInputGenerator(new ConfigurationSettingFileInput(conf.inputFolderPath + conf.inputDatasetName + conf.inputFileEnding, true, conf.inputFileSeparator, conf.inputFileQuotechar, conf.inputFileEscape, conf.inputFileStrictQuotes, conf.inputFileIgnoreLeadingWhiteSpace, conf.inputFileSkipLines, conf.inputFileHasHeader, conf.inputFileSkipDifferingLines, conf.inputFileNullString)));
            } else {
                for (String datasetName : conf.datasetNames) {
                    inputGenerators.add(new DefaultFileInputGenerator(new ConfigurationSettingFileInput(conf.inputFolderPath + datasetName + conf.inputFileEnding, true, conf.inputFileSeparator, conf.inputFileQuotechar, conf.inputFileEscape, conf.inputFileStrictQuotes, conf.inputFileIgnoreLeadingWhiteSpace, conf.inputFileSkipLines, conf.inputFileHasHeader, conf.inputFileSkipDifferingLines, conf.inputFileNullString)));
                }
            }

            List<ColumnIdentifier> columns = new ArrayList<>();
            for (RelationalInputGenerator inputGenerator : inputGenerators) {
                columns.addAll(getAcceptedColumns(inputGenerator));
            }
            ResultCache resultReceiver = new ResultCache("MetanomeMock", columns);

            InclusionDependencyAlgorithm algorithm = null;
            int editDistanceThreshold = 1;
            if (conf.algorithm == Config.Algorithm.SAWFISH) {
                SawfishInterface sawfish = new SawfishInterface();
                sawfish.setRelationalInputConfigurationValue(SawfishInterface.Identifier.INPUT_FILES.name(), inputGenerators.toArray(new RelationalInputGenerator[0]));
                sawfish.setIntegerConfigurationValue(SawfishInterface.Identifier.editDistanceThreshold.name(), editDistanceThreshold);
                sawfish.setBooleanConfigurationValue(SawfishInterface.Identifier.ignoreShortStrings.name(), false);
                sawfish.setBooleanConfigurationValue(SawfishInterface.Identifier.measureTime.name(), false);
                sawfish.setBooleanConfigurationValue(SawfishInterface.Identifier.ignoreNumericColumns.name(), false);
                //sawfish.setStringConfigurationValue(SawfishInterface.Identifier.similarityThreshold.name(), "0.9");
                //sawfish.setBooleanConfigurationValue(SawfishInterface.Identifier.hybridMode.name(), true);
                sawfish.setResultReceiver(resultReceiver);
                sawfish.setTempFileGenerator(new TempFileGenerator());
                algorithm = sawfish;
            }

            assert algorithm != null;
            long runtime = System.currentTimeMillis();
            algorithm.execute();
            runtime = System.currentTimeMillis() - runtime;

            System.out.println(runtime);

            writeResults(conf, resultReceiver, algorithm, runtime);
        } catch (AlgorithmExecutionException | IOException e) {
            e.printStackTrace();
        }
    }

    private static List<ColumnIdentifier> getAcceptedColumns(RelationalInputGenerator relationalInputGenerator) throws InputGenerationException, AlgorithmConfigurationException {
        List<ColumnIdentifier> acceptedColumns = new ArrayList<>();
        RelationalInput relationalInput = relationalInputGenerator.generateNewCopy();
        String tableName = relationalInput.relationName();
        for (String columnName : relationalInput.columnNames())
            acceptedColumns.add(new ColumnIdentifier(tableName, columnName));
        return acceptedColumns;
    }

    private static void writeResults(Config conf, ResultCache resultReceiver, Object algorithm, long runtime) throws IOException {
        if (conf.writeResults) {
            String outputPath = conf.measurementsFolderPath + conf.inputDatasetName + "_" + algorithm.getClass().getSimpleName() + File.separator;
            List<Result> results = resultReceiver.fetchNewResults();

            FileUtils.writeToFile(algorithm.toString() + "\r\n\r\n" + conf.toString() + "\r\n\r\n" + "Runtime: " + runtime + "\r\n\r\n" + "Results: " + results.size(), outputPath + conf.statisticsFileName);
            FileUtils.writeToFile(format(results), outputPath + conf.resultFileName);
        }
    }

    private static String format(List<Result> results) {
        StringBuilder builder = new StringBuilder();
        for (Result result : results) {
            InclusionDependency ind = (InclusionDependency) result;
            builder.append(ind.toString()).append("\r\n");
        }
        return builder.toString();
    }
}
