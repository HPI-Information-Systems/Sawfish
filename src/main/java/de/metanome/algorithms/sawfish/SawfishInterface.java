package de.metanome.algorithms.sawfish;

import de.metanome.algorithm_integration.AlgorithmConfigurationException;
import de.metanome.algorithm_integration.algorithm_execution.FileGenerator;
import de.metanome.algorithm_integration.algorithm_types.*;
import de.metanome.algorithm_integration.configuration.*;
import de.metanome.algorithm_integration.input.RelationalInputGenerator;
import de.metanome.algorithm_integration.result_receiver.InclusionDependencyResultReceiver;

import java.util.ArrayList;
import java.util.Arrays;

public class SawfishInterface extends Sawfish
        implements InclusionDependencyAlgorithm, RelationalInputParameterAlgorithm, IntegerParameterAlgorithm, BooleanParameterAlgorithm, StringParameterAlgorithm, TempFileAlgorithm {

    public enum Identifier {
        editDistanceThreshold, INPUT_FILES, ignoreShortStrings, memoryCheckFrequency, maxMemoryUsagePercentage, writeDataErrors, measureTime, ignoreNumericColumns, similarityThreshold, hybridMode
    }

    @Override
    public ArrayList<ConfigurationRequirement<?>> getConfigurationRequirements() {
        ArrayList<ConfigurationRequirement<?>> conf = new ArrayList<>();
        conf.add(new ConfigurationRequirementRelationalInput(Identifier.INPUT_FILES.name(), ConfigurationRequirement.ARBITRARY_NUMBER_OF_VALUES));

        ConfigurationRequirementInteger editDistanceThreshold = new ConfigurationRequirementInteger(Identifier.editDistanceThreshold.name());
        Integer[] defaultIntegerParameter = {0};
        editDistanceThreshold.setDefaultValues(defaultIntegerParameter);
        conf.add(editDistanceThreshold);
        ConfigurationRequirementString similarityThreshold = new ConfigurationRequirementString(Identifier.similarityThreshold.name());
        String[] defaultStringParamerter = {"0.0"};
        similarityThreshold.setDefaultValues(defaultStringParamerter);
        conf.add(similarityThreshold);
        // Compatibility Option for Baseline
        ConfigurationRequirementBoolean ignoreShortStrings = new ConfigurationRequirementBoolean(Identifier.ignoreShortStrings.name());
        Boolean[] ignoreShortStringsDefault = {true};
        ignoreShortStrings.setDefaultValues(ignoreShortStringsDefault);
        conf.add(ignoreShortStrings);
        ConfigurationRequirementBoolean showErrors = new ConfigurationRequirementBoolean(Identifier.writeDataErrors.name());
        Boolean[] defaultBooleanParameter = {false};
        showErrors.setDefaultValues(defaultBooleanParameter);
        conf.add(showErrors);
        ConfigurationRequirementBoolean measureTime = new ConfigurationRequirementBoolean(Identifier.measureTime.name());
        measureTime.setDefaultValues(defaultBooleanParameter);
        conf.add(measureTime);
        ConfigurationRequirementBoolean ignoreNumericColumns = new ConfigurationRequirementBoolean(Identifier.ignoreNumericColumns.name());
        ignoreNumericColumns.setDefaultValues(defaultBooleanParameter);
        conf.add(ignoreNumericColumns);
        ConfigurationRequirementInteger memoryCheckFrequency = new ConfigurationRequirementInteger(Identifier.memoryCheckFrequency.name());
        Integer[] defaultMemoryCheckFrequency = {100};
        memoryCheckFrequency.setDefaultValues(defaultMemoryCheckFrequency);
        conf.add(memoryCheckFrequency);
        ConfigurationRequirementInteger maxMemoryUsage = new ConfigurationRequirementInteger(Identifier.maxMemoryUsagePercentage.name());
        Integer[] defaultMaxMemoryUsage = {80};
        maxMemoryUsage.setDefaultValues(defaultMaxMemoryUsage);
        conf.add(maxMemoryUsage);
        ConfigurationRequirementBoolean hybridMode = new ConfigurationRequirementBoolean(Identifier.hybridMode.name());
        hybridMode.setDefaultValues(defaultBooleanParameter);
        conf.add(hybridMode);

        return conf;
    }

    @Override
    public String getAuthors() {
        return "Youri Kaminsky";
    }

    @Override
    public String getDescription() {
        return "SAWFISH is the first algorithm to efficiently discover Similarity Inclusion Dependency Discovery";
    }

    @Override
    public void setResultReceiver(
            InclusionDependencyResultReceiver resultReceiver) {
        this.resultReceiver = resultReceiver;
    }

    @Override
    public void setTempFileGenerator(FileGenerator tempFileGenerator) {
        this.tempFileGenerator = tempFileGenerator;
    }

    @Override
    public void setRelationalInputConfigurationValue(String identifier, RelationalInputGenerator... values) throws AlgorithmConfigurationException {
        if (identifier.equals(Identifier.INPUT_FILES.name())) {
            this.inputGenerators = new ArrayList<>(Arrays.asList(values));
        } else {
            throw new AlgorithmConfigurationException();
        }
    }

    @Override
    public void setIntegerConfigurationValue(String identifier, Integer... values) throws AlgorithmConfigurationException {
        if (identifier.equals(Identifier.editDistanceThreshold.name())) {
            if (this.editDistanceManager == null || this.editDistanceManager.isNullInitialized()) {
                this.editDistanceManager = new EditDistanceManager(values[0]);
            } else if (values[0] != 0) {
                throw new AlgorithmConfigurationException("Please use either an absolute or a normalized edit distance.");
            }
        } else if (identifier.equals(Identifier.memoryCheckFrequency.name())) {
            this.memoryCheckFrequency = values[0];
        } else if (identifier.equals(Identifier.maxMemoryUsagePercentage.name())) {
            this.maxMemoryUsagePercentage = values[0];
        } else {
            throw new AlgorithmConfigurationException("Unknown identifier: " + identifier);
        }
    }

    @Override
    public void setBooleanConfigurationValue(String identifier, Boolean... values) throws AlgorithmConfigurationException {
        if (identifier.equals(Identifier.ignoreShortStrings.name())) {
            this.ignoreShortStrings = values[0];
        } else if (identifier.equals(Identifier.writeDataErrors.name())) {
            this.showErrors = values[0];
        } else if (identifier.equals(Identifier.measureTime.name())) {
            this.measureTime = values[0];
        } else if (identifier.equals(Identifier.ignoreNumericColumns.name())) {
            this.ignoreNumericColumns = values[0];
        } else if (identifier.equals(Identifier.hybridMode.name())) {
            this.hybridMode = values[0];
        } else {
            throw new AlgorithmConfigurationException("Unknown identifier: " + identifier);
        }
    }

    @Override
    public void setStringConfigurationValue(String identifier, String... values) throws AlgorithmConfigurationException {
        if (identifier.equals(Identifier.similarityThreshold.name())) {
            float simThreshold = Float.parseFloat(values[0]);
            if (this.editDistanceManager == null || (this.editDistanceManager.isNullInitialized() && simThreshold != 0f)) {
                this.editDistanceManager = new EditDistanceManager(simThreshold);
            } else if (simThreshold != 0f) {
                throw new AlgorithmConfigurationException("Please use either an absolute or a normalized edit distance.");
            }
        } else {
            throw new AlgorithmConfigurationException("Unknown identifier: " + identifier);
        }
    }


}
