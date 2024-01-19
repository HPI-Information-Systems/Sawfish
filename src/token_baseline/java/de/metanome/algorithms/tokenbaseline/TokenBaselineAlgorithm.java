package de.metanome.algorithms.tokenbaseline;

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

public class TokenBaselineAlgorithm {

    protected ArrayList<RelationalInputGenerator> inputGenerators = null;
    protected InclusionDependencyResultReceiver resultReceiver = null;
    protected float similarityThreshold = 1.0f;
    private final ArrayList<String[]> indexToRelationColumn = new ArrayList<>();

    public void execute() throws AlgorithmExecutionException {
        long start = System.nanoTime();
        int columnOffset = 0;
        HashSet<Integer> deletedColumns = new HashSet<>();
        ArrayList<HashSet<ArrayList<String>>> columnInputs = new ArrayList<>();

        for (RelationalInputGenerator inputGenerator : inputGenerators) {
            RelationalInput input = inputGenerator.generateNewCopy();
            for (int i = 0; i < input.numberOfColumns(); i++) {
                columnInputs.add(new HashSet<>());
                indexToRelationColumn.add(new String[]{input.relationName(), input.columnNames().get(i)});
            }
            int index;
            while (input.hasNext()) {
                List<String> row = input.next();
                index = 0;
                for (String s : row) {
                    if (s != null && !deletedColumns.contains(columnOffset + index)) {
                        String[] tokens = s.split("\\s+");
                        if (s.length() > 50 || tokens.length > 10) {
                            deletedColumns.add(columnOffset + index);
                        }
                        columnInputs.get(columnOffset + index).add(new ArrayList<>(Arrays.asList(tokens)));
                    }
                    index++;
                }
            }
            columnOffset += input.numberOfColumns();
        }

        long inputDone = System.nanoTime();
        System.out.println("input reading: " + (inputDone - start));

        for (int referencedColumn = 0; referencedColumn < columnInputs.size(); referencedColumn++) {
            if (columnInputs.get(referencedColumn).size() == 0 || deletedColumns.contains(referencedColumn))
                continue;
            HashMap<String, ArrayList<ArrayList<String>>> index = new HashMap<>();
            for (ArrayList<String> tokens : columnInputs.get(referencedColumn)) {
                for (String t : tokens) {
                    index.computeIfAbsent(t, s -> new ArrayList<>()).add(tokens);
                }
            }
            for (int dependentColumn = 0; dependentColumn < columnInputs.size(); dependentColumn++) {
                if (dependentColumn == referencedColumn || deletedColumns.contains(dependentColumn))
                    continue;

                boolean isValidIND = true;
                HashSet<ArrayList<String>> columnValues = columnInputs.get(dependentColumn);
                for (ArrayList<String> v : columnValues) {
                    boolean isValidValue = false;
                    HashMap<ArrayList<String>, Integer> counts = new HashMap<>();
                    int minThreshold = (int) Math.ceil(similarityThreshold / (1 + similarityThreshold) * (v.size() + 1));
                    for (String t : v) {
                        ArrayList<ArrayList<String>> matches = index.get(t);
                        if (matches != null) {
                            for (ArrayList<String> match : matches) {
                                counts.putIfAbsent(match, 0);
                                counts.put(match, counts.get(match) + 1);
                                if (counts.get(match) >= minThreshold && getJaccardSimilarity(v, match) >= similarityThreshold) {
                                    isValidValue = true;
                                    break;
                                }
                            }
                            if (isValidValue) break;
                        }
                    }
                    if (!isValidValue) {
                        isValidIND = false;
                        break;
                    }
                }

                if (isValidIND) {
                    resultReceiver.receiveResult(new InclusionDependency(getColumnPermutationByIndex(dependentColumn), getColumnPermutationByIndex(referencedColumn)));
                }
            }
        }

        System.out.println("validation: " + (System.nanoTime() - inputDone));
    }

    private ColumnPermutation getColumnPermutationByIndex(Integer index) {
        String[] columnId = indexToRelationColumn.get(index);
        return new ColumnPermutation(new ColumnIdentifier(columnId[0], columnId[1]));
    }

    @Override
    public String toString() {
        return this.getClass().getName();
    }

    private float getJaccardSimilarity(ArrayList<String> s1, ArrayList<String> s2) {
        HashSet<String> s1Set = new HashSet<>(s1);
        HashSet<String> s2Set = new HashSet<>(s2);

        float count = 0;
        for (String s : s2Set) {
            if (s1Set.contains(s)) count++;
        }
        return (count) / (s1Set.size() + s2Set.size() - count);
    }
}
