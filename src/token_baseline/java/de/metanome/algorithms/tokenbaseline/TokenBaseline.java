package de.metanome.algorithms.tokenbaseline;

import java.util.ArrayList;
import java.util.Arrays;

import de.metanome.algorithm_integration.AlgorithmConfigurationException;
import de.metanome.algorithm_integration.algorithm_types.*;
import de.metanome.algorithm_integration.configuration.ConfigurationRequirement;
import de.metanome.algorithm_integration.configuration.ConfigurationRequirementRelationalInput;
import de.metanome.algorithm_integration.configuration.ConfigurationRequirementString;
import de.metanome.algorithm_integration.input.RelationalInputGenerator;
import de.metanome.algorithm_integration.result_receiver.InclusionDependencyResultReceiver;

public class TokenBaseline extends TokenBaselineAlgorithm implements InclusionDependencyAlgorithm, RelationalInputParameterAlgorithm, StringParameterAlgorithm {


    @Override
    public void setStringConfigurationValue(String identifier, String... values) throws AlgorithmConfigurationException {
        if (identifier.equals(Identifier.similarityThreshold.name())) {
            this.similarityThreshold = Float.parseFloat(values[0]);
        } else {
            throw new AlgorithmConfigurationException("Unknown option");
        }
    }

    public enum Identifier {
        similarityThreshold, INPUT_FILES
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

        ConfigurationRequirementString similarityThreshold = new ConfigurationRequirementString(Identifier.similarityThreshold.name());
        String[] stringStandard = {"0.0"};
        similarityThreshold.setDefaultValues(stringStandard);
        similarityThreshold.setRequired(true);
        conf.add(similarityThreshold);

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
}
