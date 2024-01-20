package de.metanome.algorithms.sindbaseline;

import java.util.*;

import de.metanome.algorithm_integration.AlgorithmConfigurationException;
import de.metanome.algorithm_integration.AlgorithmExecutionException;
import de.metanome.algorithm_integration.ColumnIdentifier;
import de.metanome.algorithm_integration.ColumnPermutation;
import de.metanome.algorithm_integration.input.InputGenerationException;
import de.metanome.algorithm_integration.input.InputIterationException;
import de.metanome.algorithm_integration.input.RelationalInput;
import de.metanome.algorithm_integration.input.RelationalInputGenerator;
import de.metanome.algorithm_integration.result_receiver.ColumnNameMismatchException;
import de.metanome.algorithm_integration.result_receiver.CouldNotReceiveResultException;
import de.metanome.algorithm_integration.result_receiver.InclusionDependencyResultReceiver;
import de.metanome.algorithm_integration.result_receiver.OrderDependencyResultReceiver;
import de.metanome.algorithm_integration.results.InclusionDependency;
import de.metanome.algorithm_integration.results.OrderDependency;
import de.metanome.algorithms.sindbaseline.editdistanceclusterer.EditDistanceJoinResult;
import de.metanome.algorithms.sindbaseline.editdistanceclusterer.EditDistanceJoiner;

public class SINDBaselineAlgorithm {

    protected ArrayList<RelationalInputGenerator> inputGenerators = null;
    protected InclusionDependencyResultReceiver resultReceiver = null;
    protected int errorDistance;
    private final ArrayList<EditDistanceJoiner> columnIndexes = new ArrayList<>();
    private final ArrayList<String[]> indexToRelationColumn = new ArrayList<>();

    public void execute() throws AlgorithmExecutionException {
        int columnOffset = 0;
        ArrayList<Integer> smallestLength = new ArrayList<>();
        ArrayList<Integer> longestLength = new ArrayList<>();
        HashSet<Integer> deletedColumns = new HashSet<>();

        for (RelationalInputGenerator inputGenerator : inputGenerators) {
            RelationalInput input = inputGenerator.generateNewCopy();
            ArrayList<HashSet<String>> columnInputs = new ArrayList<>(input.numberOfColumns());
            for (int i = 0; i < input.numberOfColumns(); i++) {
                columnInputs.add(new HashSet<>());
                indexToRelationColumn.add(new String[]{input.relationName(), input.columnNames().get(i)});
                smallestLength.add(51);
                longestLength.add(0);
            }
            int index;
            while (input.hasNext()) {
                List<String> row = input.next();
                index = 0;
                for (String s : row) {
                    if (s != null && s.length() > errorDistance && !deletedColumns.contains(columnOffset + index)) {
                        if (s.length() > 50) {
                            deletedColumns.add(columnOffset + index);
                        }
                        if (columnInputs.get(index).add(s)) {
                            if (s.length() < smallestLength.get(columnOffset + index)) {
                                smallestLength.set(columnOffset + index, s.length());
                            }
                            if (s.length() > longestLength.get(columnOffset + index)) {
                                longestLength.set(columnOffset + index, s.length());
                            }
                        }
                    }
                    index++;
                }
            }
            for (int i = 0; i < input.numberOfColumns(); i++) {

                EditDistanceJoiner editDistanceJoiner = new EditDistanceJoiner(errorDistance);
                if (!deletedColumns.contains(columnOffset + i)) {
                    for (String s : columnInputs.get(i)) {
                        editDistanceJoiner.populate(s);
                    }
                    editDistanceJoiner.indexAllStrings();
                }
                columnIndexes.add(editDistanceJoiner);
            }
            columnOffset += input.numberOfColumns();
        }

        for (int dependentColumn = 0; dependentColumn < columnIndexes.size(); dependentColumn++) {
            if (columnIndexes.get(dependentColumn).getAllStrings().size() <= 1 || deletedColumns.contains(dependentColumn))
                continue;
            for (int referencedColumn = 0; referencedColumn < columnIndexes.size(); referencedColumn++) {
                if (dependentColumn == referencedColumn || deletedColumns.contains(referencedColumn) || smallestLength.get(dependentColumn) < smallestLength.get(referencedColumn) - errorDistance || longestLength.get(dependentColumn) > longestLength.get(referencedColumn) + errorDistance)
                    continue;

                boolean isValidIND = true;
                // we dont want to look at index 0 as we need to reserve it for the lookup
                List<String> columnValues = columnIndexes.get(dependentColumn).getAllStrings();
                for (String s : columnValues.subList(1, columnValues.size())) {
                    if (!columnIndexes.get(referencedColumn).hasJoinPartners(s)) {
                        isValidIND = false;
                        break;
                    }
                }

                if (isValidIND) {
                    resultReceiver.receiveResult(new InclusionDependency(getColumnPermutationByIndex(dependentColumn), getColumnPermutationByIndex(referencedColumn)));
                }
            }
        }
    }

    private ColumnPermutation getColumnPermutationByIndex(Integer index) {
        String[] columnId = indexToRelationColumn.get(index);
        return new ColumnPermutation(new ColumnIdentifier(columnId[0], columnId[1]));
    }

    @Override
    public String toString() {
        return this.getClass().getName();
    }
}
