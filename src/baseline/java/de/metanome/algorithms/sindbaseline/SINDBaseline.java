package de.metanome.algorithms.sindbaseline;

import java.util.ArrayList;
import java.util.Arrays;

import de.metanome.algorithm_integration.AlgorithmConfigurationException;
import de.metanome.algorithm_integration.algorithm_types.*;
import de.metanome.algorithm_integration.configuration.ConfigurationRequirement;
import de.metanome.algorithm_integration.configuration.ConfigurationRequirementInteger;
import de.metanome.algorithm_integration.configuration.ConfigurationRequirementRelationalInput;
import de.metanome.algorithm_integration.input.RelationalInputGenerator;
import de.metanome.algorithm_integration.result_receiver.InclusionDependencyResultReceiver;

public class SINDBaseline extends SINDBaselineAlgorithm implements InclusionDependencyAlgorithm, RelationalInputParameterAlgorithm, IntegerParameterAlgorithm {


    public enum Identifier {
        editDistanceThreshold, INPUT_FILES
    }

    @Override
    public String getAuthors() {
        return "Youri Kaminsky";
    }

    @Override
    public String getDescription() {
        return "A Baseline that provides a lower bound for sIND detection";
    }

    @Override
    public void setResultReceiver(InclusionDependencyResultReceiver resultReceiver) {
        this.resultReceiver = resultReceiver;
    }

    @Override
    public ArrayList<ConfigurationRequirement<?>> getConfigurationRequirements() {
        ArrayList<ConfigurationRequirement<?>> conf = new ArrayList<>();
        conf.add(new ConfigurationRequirementRelationalInput(Identifier.INPUT_FILES.name(), ConfigurationRequirement.ARBITRARY_NUMBER_OF_VALUES));

        ConfigurationRequirementInteger errorDistance = new ConfigurationRequirementInteger(Identifier.editDistanceThreshold.name());
        Integer[] defaultIntegerParameter = new Integer[1];
        defaultIntegerParameter[0] = 1;
        errorDistance.setDefaultValues(defaultIntegerParameter);
        errorDistance.setRequired(true);
        conf.add(errorDistance);

        return conf;
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
    public void setIntegerConfigurationValue(String identifier, Integer... values) {
        if (identifier.equals(Identifier.editDistanceThreshold.name())) {
            this.errorDistance = values[0];
        }
    }
}
