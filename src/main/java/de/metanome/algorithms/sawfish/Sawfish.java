package de.metanome.algorithms.sawfish;

import de.metanome.algorithm_integration.AlgorithmExecutionException;
import de.metanome.algorithm_integration.ColumnIdentifier;
import de.metanome.algorithm_integration.ColumnPermutation;
import de.metanome.algorithm_integration.algorithm_execution.FileGenerator;
import de.metanome.algorithm_integration.input.RelationalInput;
import de.metanome.algorithm_integration.input.RelationalInputGenerator;
import de.metanome.algorithm_integration.result_receiver.InclusionDependencyResultReceiver;
import de.metanome.algorithm_integration.results.InclusionDependency;

import java.io.*;
import java.lang.management.GarbageCollectorMXBean;
import java.lang.management.ManagementFactory;
import java.util.*;

public class Sawfish {
    protected ArrayList<RelationalInputGenerator> inputGenerators = null;
    protected InclusionDependencyResultReceiver resultReceiver = null;
    protected boolean ignoreShortStrings = true;
    protected int memoryCheckFrequency = 100;
    protected int maxMemoryUsagePercentage = 70;
    protected boolean showErrors = false;
    protected boolean measureTime = false;
    protected boolean ignoreNumericColumns = false;
    long availableMemory = ManagementFactory.getMemoryMXBean().getHeapMemoryUsage().getMax();
    long maxMemoryUsage = (long) (availableMemory * (maxMemoryUsagePercentage / 100.0f));
    protected FileGenerator tempFileGenerator;
    protected int absoluteEditDistance = 0;
    protected float similarityThreshold = 0f;
    protected boolean hybridMode = false;
    protected boolean tokenMode = false;
    SimilarityMeasureManager similarityMeasureManager = null;

    protected final ArrayList<String[]> indexToRelationColumn = new ArrayList<>();
    protected ArrayList<InvertedIndex> invertedIndexByColumn;
    private final ArrayList<HashMap<Integer, File>> columnLengthFiles = new ArrayList<>();
    private final ArrayList<ColumnStats> columnStats = new ArrayList<>();
    private final ArrayList<HashMap<Integer, ArrayList<SubstringableString>>> allValues = new ArrayList<>();
    private final ArrayList<Long> columnSizes = new ArrayList<>();
    HashSet<Integer> needsDeduplication = new HashSet<>();
    HashSet<Integer> markAsDeleted = new HashSet<>();
    int smallestLength = Integer.MAX_VALUE;
    int longestLength = 0;
    boolean writtenToFile = false;
    ArrayList<HashSet<Integer>> possibleDependentsList;
    int[] possibleReferences;
    ArrayList<TimingStats> timingStats = null;
    HashMap<Integer, HashMap<Integer, LinkedList<InvertedSegmentIndex.NonDirectMatch>>> errors = null;

    public void execute() throws AlgorithmExecutionException {
        this.similarityMeasureManager = new SimilarityMeasureManager(absoluteEditDistance, similarityThreshold, hybridMode, tokenMode);

        int numAllColumns = readInput();
        generateCandidates(numAllColumns);
        initializeOtherDataStructures(numAllColumns);
        System.out.println("Preprocessing done!");

        long indexingTime = validateCandidates(numAllColumns);
        outputResults(numAllColumns, indexingTime);
    }

    private void outputResults(int numAllColumns, long indexingTime) throws AlgorithmExecutionException {
        // output results
        for (int columnIndex = 0; columnIndex < numAllColumns; columnIndex++) {
            ColumnPermutation referencedColumnIndex = getColumnPermutationByIndex(columnIndex);
            for (Integer dependentColumnIndex : possibleDependentsList.get(columnIndex)) {
                resultReceiver.receiveResult(new InclusionDependency(getColumnPermutationByIndex(dependentColumnIndex), referencedColumnIndex));
            }
        }

        if (measureTime && timingStats != null) {
            System.out.println("Writing timing stats to disk");
            long sum = 0L;
            for (GarbageCollectorMXBean gc : ManagementFactory.getGarbageCollectorMXBeans()) {
                sum += gc.getCollectionCount();
            }
            System.out.println("Needed to gc " + sum + " times");
            writeTimingStatsToFile(timingStats, indexingTime);
        }

        if (showErrors) {
            System.out.println("Writing non-direct matches to disk");
            writeErrorsToFile(errors);
        }
    }


    private int readInput() throws AlgorithmExecutionException {
        // deduplicate columns and generate length statistics
        int columnOffset = 0;
        int numValuesSinceLastMemoryCheck = 0;
        for (RelationalInputGenerator inputGenerator : inputGenerators) {
            RelationalInput input = inputGenerator.generateNewCopy();
            int[] numValuesInColumn = new int[input.numberOfColumns()];
            long[] currColumnSizes = new long[input.numberOfColumns()];
            ArrayList<HashMap<Integer, HashSet<SubstringableString>>> deduplicatedColumns = new ArrayList<>(input.numberOfColumns());
            for (int i = 0; i < input.numberOfColumns(); i++) {
                indexToRelationColumn.add(columnOffset + i, new String[]{input.relationName(), input.columnNames().get(i)});
                columnStats.add(new ColumnStats());
                allValues.add(new HashMap<>());
                columnLengthFiles.add(new HashMap<>());
                currColumnSizes[i] = 0L;
                deduplicatedColumns.add(new HashMap<>());
            }
            while (input.hasNext()) {
                List<String> curr = input.next();
                int index = 0;
                for (String el : curr) {
                    if (el != null && !markAsDeleted.contains(columnOffset + index)) {
                        ColumnStats stats = columnStats.get(columnOffset + index);
                        if (el.length() > 50) {
                            markAsDeleted.add(columnOffset + index);
                            stats.longestLength = 0;
                            deduplicatedColumns.get(index).clear();
                            index++;
                            continue;
                        }
                        SubstringableString string;
                        if (tokenMode) {
                            string = new TokenizedString(el.trim().toCharArray());
                        } else {
                             string = new SubstringableString(el.trim());
                        }
                        int elLength = string.elLength();

                        if ((tokenMode || (!ignoreShortStrings || elLength > similarityMeasureManager.getActualEditDistanceForLength(string.length()))) && deduplicatedColumns.get(index).computeIfAbsent(elLength, l -> new HashSet<>()).add(string)) {
                            if (tokenMode && elLength > 10) {
                                markAsDeleted.add(columnOffset + index);
                                stats.longestLength = 0;
                                deduplicatedColumns.get(index).clear();
                            } else {
                                numValuesSinceLastMemoryCheck++;
                                numValuesInColumn[index]++;
                                int numSegments = tokenMode ? elLength : similarityMeasureManager.getMaximumSegmentCountForLength(elLength);
                                currColumnSizes[index] += 8 * ((2L * string.getUnderlyingChars().length / 8) + 1) + 64 + numSegments * 8L;
                                if (elLength < stats.shortestLength) stats.shortestLength = elLength;
                                if (elLength > stats.longestLength) stats.longestLength = elLength;
                                if (ignoreNumericColumns) {
                                    if (stats.canBeInteger) try {
                                        Integer.parseInt(string.toString());
                                    } catch (NumberFormatException e) {
                                        stats.canBeInteger = false;
                                    }
                                    if (ignoreNumericColumns && stats.canBeFloat) try {
                                        Float.parseFloat(string.toString());
                                    } catch (NumberFormatException e) {
                                        stats.canBeFloat = false;
                                    }
                                }
                            }
                        }
                    }
                    index++;
                }

                if (numValuesSinceLastMemoryCheck >= memoryCheckFrequency) {
                    numValuesSinceLastMemoryCheck = 0;

                    while (ManagementFactory.getMemoryMXBean().getHeapMemoryUsage().getUsed() > maxMemoryUsage) {
                        System.gc();
                        if (ManagementFactory.getMemoryMXBean().getHeapMemoryUsage().getUsed() <= maxMemoryUsage) break;
                        writtenToFile = true;
                        // Identify largest buffer
                        for (int columnIndex = 0; columnIndex < columnOffset; columnIndex++) {
                            writeColumnArrayToDisk(needsDeduplication, allValues.get(columnIndex), columnIndex);
                            allValues.set(columnIndex, new HashMap<>());
                        }
                        System.gc();
                        if (ManagementFactory.getMemoryMXBean().getHeapMemoryUsage().getUsed() <= maxMemoryUsage) break;

                        int largestColumnNumber = 0;
                        int largestColumnSize = numValuesInColumn[largestColumnNumber];
                        for (int otherColumnNumber = 1; otherColumnNumber < input.numberOfColumns(); otherColumnNumber++) {
                            if (largestColumnSize < numValuesInColumn[otherColumnNumber]) {
                                largestColumnNumber = otherColumnNumber;
                                largestColumnSize = numValuesInColumn[largestColumnNumber];
                            }
                        }

                        numValuesInColumn[largestColumnNumber] = 0;

                        System.out.println("Had to write column " + (columnOffset + largestColumnNumber) + " to disk");

                        writeColumnSetToDisk(needsDeduplication, deduplicatedColumns.get(largestColumnNumber), columnOffset + largestColumnNumber);
                        deduplicatedColumns.set(largestColumnNumber, new HashMap<>());
                        System.gc();
                    }
                }
            }

            for (int columnIdx = 0; columnIdx < input.numberOfColumns(); columnIdx++) {
                for (Map.Entry<Integer, HashSet<SubstringableString>> length2Values : deduplicatedColumns.get(columnIdx).entrySet()) {
                    allValues.get(columnOffset + columnIdx).put(length2Values.getKey(), new ArrayList<>(length2Values.getValue()));
                }
            }

            columnOffset += input.numberOfColumns();

            for (long size : currColumnSizes) {
                columnSizes.add(size);
            }
        }

        // if we need to write to disk, then write everything to disk
        if (writtenToFile) {
            for (int columnIndex = 0; columnIndex < columnOffset; columnIndex++) {
                writeColumnArrayToDisk(needsDeduplication, allValues.get(columnIndex), columnIndex);
            }
            System.gc();
        }

        System.out.println("All columns: " + indexToRelationColumn.size());
        System.out.println("Deleted columns: " + markAsDeleted.size());
        for (Integer column : markAsDeleted) {
            System.out.println(getColumnPermutationByIndex(column));
        }

        System.out.println("Read all input!");

        if (writtenToFile) {
            for (Integer column : needsDeduplication) {
                long sum = 0L;
                for (Map.Entry<Integer, File> length2File : columnLengthFiles.get(column).entrySet()) {
                    HashSet<SubstringableString> deduplicatedValues = new HashSet<>();
                    Scanner reader;
                    try {
                        reader = new Scanner(length2File.getValue());
                    } catch (FileNotFoundException e) {
                        e.printStackTrace();
                        throw new AlgorithmExecutionException("Temp file reading did not work");
                    }
                    while (reader.hasNextLine()) {
                        SubstringableString nextLine = new SubstringableString(reader.nextLine());
                        if (tokenMode) {
                            nextLine = nextLine.toTokenizedString();
                        }
                        if (deduplicatedValues.add(nextLine)) {
                            int numSegments = tokenMode ? nextLine.elLength() : similarityMeasureManager.getMaximumSegmentCountForLength(nextLine.length());
                            sum += 8 * ((2L * nextLine.getUnderlyingChars().length / 8) + 1) + 64 + numSegments * 8L;
                        }
                    }
                    writeToFile(length2File.getValue(), deduplicatedValues, false);
                }
                columnSizes.set(column, sum);
            }
        }

        System.out.println("Deduplication done");

        return columnOffset;
    }

    private void generateCandidates(int numAllColumns) {
        possibleReferences = new int[numAllColumns];
        possibleDependentsList = new ArrayList<>(numAllColumns);

        for (int i = 0; i < numAllColumns; i++) {
            possibleReferences[i] = numAllColumns - 1;
            if (ignoreNumericColumns) {
                if (columnStats.get(i).canBeInteger || columnStats.get(i).canBeFloat) {
                    markAsDeleted.add(i);
                    columnStats.get(i).longestLength = 0;
                    allValues.get(i).clear();
                }
                System.gc();
            }
        }

        for (int columnIndex = 0; columnIndex < numAllColumns; columnIndex++) {
            // all other columns might be referencing the current column, except the column itself
            HashSet<Integer> currentDependents = getColumnSets(numAllColumns, columnIndex);

            ColumnStats ownLengthStat = columnStats.get(columnIndex);
            if (!tokenMode && ownLengthStat.shortestLength <= similarityMeasureManager.getActualEditDistanceForLength(ownLengthStat.shortestLength)) {
                ownLengthStat.hasShortValue = true;
            }

            if (ownLengthStat.longestLength == 0) {
                // empty column
                currentDependents.clear();
                markAsDeleted.add(columnIndex);
            } else {
                // prune candidate columns based on length stats
                for (int j = 0; j < numAllColumns; j++) {
                    if (j == columnIndex) continue;
                    ColumnStats otherLengthStat = columnStats.get(j);
                    // handle empty columns
                    if (otherLengthStat.longestLength == 0) continue;

                    // exclude simple sINDs
                    if (!tokenMode && ownLengthStat.longestLength <= similarityMeasureManager.getActualEditDistanceForLength(ownLengthStat.longestLength) && otherLengthStat.longestLength <= similarityMeasureManager.getActualEditDistanceForLength(otherLengthStat.longestLength)) {
                        currentDependents.remove(j);
                        possibleReferences[j]--;
                        continue;
                    }

                    // apply length pruning
                    if (ownLengthStat.shortestLength > otherLengthStat.shortestLength + similarityMeasureManager.getMaximumEditDistanceForLength(otherLengthStat.shortestLength)) {
                        currentDependents.remove(j);
                        possibleReferences[j]--;
                        continue;
                    }

                    if (ownLengthStat.longestLength < otherLengthStat.longestLength - similarityMeasureManager.getMaximumEditDistanceForLength(otherLengthStat.longestLength)) {
                        currentDependents.remove(j);
                        possibleReferences[j]--;
                    }
                }
            }

            possibleDependentsList.add(currentDependents);
        }

        for (int i = 0; i < numAllColumns; i++) {
            possibleDependentsList.get(i).removeAll(markAsDeleted);
            possibleReferences[i] -= markAsDeleted.size();
        }
    }

    private void initializeOtherDataStructures(int numAllColumns) {
        invertedIndexByColumn = new ArrayList<>(numAllColumns);
        if (measureTime) {
            timingStats = new ArrayList<>(numAllColumns);
        }
        if (showErrors) {
            errors = new HashMap<>(numAllColumns / 4);
        }

        for (int i = 0; i < numAllColumns; i++) {
            if (measureTime) {
                timingStats.add(new TimingStats(numAllColumns));
            }

            if (!possibleDependentsList.get(i).isEmpty()) {
                if (columnStats.get(i).shortestLength < smallestLength) {
                    smallestLength = columnStats.get(i).shortestLength;
                }

                if (columnStats.get(i).longestLength > longestLength) {
                    longestLength = columnStats.get(i).longestLength;
                }
            }

            if (tokenMode) {
                invertedIndexByColumn.add(new InvertedTokenIndex(similarityMeasureManager));
            } else {
                invertedIndexByColumn.add(new InvertedSegmentIndex(similarityMeasureManager));
            }
        }

        System.out.println("Longest length: " + longestLength);

        if (!tokenMode) {
            Utils.editDistanceBuffer = new int[longestLength][longestLength];
            for (int i = 0; i < longestLength; i++) {
                Utils.editDistanceBuffer[0][i] = i;
                Utils.editDistanceBuffer[i][0] = i;
            }
        }
    }

    private long validateCandidates(int numAllColumns) throws AlgorithmExecutionException {
        long indexingTime = 0L;
        HashSet<Integer> alreadyProcessedColumns = new HashSet<>();
        HashSet<Integer> currentReferencedColumns;

        // save candidates that need to be removed to avoid concurrent modification
        LinkedList<Integer> removals = new LinkedList<>();

        // loop until all columns are fully processed
        while (alreadyProcessedColumns.size() != numAllColumns) {
            currentReferencedColumns = getFittingColumns(alreadyProcessedColumns, possibleDependentsList, columnSizes);

            System.out.println("Current referenced columns" + currentReferencedColumns);

            long indexStart = System.nanoTime();
            for (Integer columnIndex : currentReferencedColumns) {
                InvertedIndex invertedIndex = invertedIndexByColumn.get(columnIndex);
                // set up index with all values of longestLength - editDistanceThreshold
                for (int i = longestLength; i >= longestLength - similarityMeasureManager.getMaximumEditDistanceForLength(longestLength); i--) {
                    invertedIndex.addElementsWithLength(getValuesForLength(i, columnIndex), i);
                    invertedIndex.indexByLength(i);
                }
            }

            if (measureTime) {
                indexingTime += System.nanoTime() - indexStart;
            }

            for (int currentLength = longestLength; currentLength >= smallestLength; currentLength--) {
                Iterator<SubstringableString> currentValues;
                int currEditDistance = similarityMeasureManager.getMaximumEditDistanceForLength(currentLength);
                for (int referencedColumnIndex : currentReferencedColumns) {
                    HashSet<Integer> possibleDependents = possibleDependentsList.get(referencedColumnIndex);
                    InvertedIndex currIndex = invertedIndexByColumn.get(referencedColumnIndex);
                    TimingStats t = null;
                    if (timingStats != null) {
                        t = timingStats.get(referencedColumnIndex);
                    }
                    for (Integer dependentColumnIndex : possibleDependents) {
                        if (!tokenMode && currentLength <= similarityMeasureManager.getActualEditDistanceForLength(currentLength) && columnStats.get(referencedColumnIndex).hasShortValue && columnStats.get(dependentColumnIndex).hasShortValue) {
                            // If both columns have short values, we do not need to validate any values below the editDistance
                            continue;
                        }

                        try {
                            currentValues = getValueIteratorForLength(currentLength, dependentColumnIndex, currentReferencedColumns);
                        } catch (IOException e) {
                            e.printStackTrace();
                            throw new AlgorithmExecutionException("reading failed");
                        }
                        long validationStart = System.nanoTime();
                        // for each value, check each candidate column for possible similar strings
                        while (currentValues.hasNext()) {
                            SubstringableString searchString = currentValues.next();
                            if (t != null) {
                                t.validationValues[dependentColumnIndex]++;
                            }

                            boolean candidateVerified = false;
                            for (int index = 0; index <= 2 * currEditDistance; index++) {
                                int queryLength = currentLength + getEditDistanceFromIndex(index);
                                if (queryLength <= longestLength && queryLength > 0) {
                                    candidateVerified = currIndex.existsSimilarReferencedValueForLength(searchString, queryLength, dependentColumnIndex, referencedColumnIndex, errors, t);
                                    if (candidateVerified) break;
                                }
                            }
                            // continue verifying all elements of column until one cannot be verified or all value are verified
                            if (!candidateVerified) {
                                removals.add(dependentColumnIndex);
                                break;
                            }
                        }
                        if (t != null) {
                            t.validationTimePerColumn[dependentColumnIndex] += System.nanoTime() - validationStart;
                        }
                    }
                    for (Integer removal : removals) {
                        possibleDependents.remove(removal);
                        possibleReferences[removal]--;
                    }
                    removals.clear();
                }
                indexStart = System.nanoTime();
                // read strings for next length and update indices
                for (int columnIndex : currentReferencedColumns) {
                    InvertedIndex segmentIndex = invertedIndexByColumn.get(columnIndex);
                    if (possibleDependentsList.get(columnIndex).isEmpty() && possibleReferences[columnIndex] == 0) {
                        segmentIndex.clear();
                    } else {
                        segmentIndex.removeLengthFromIndex(currentLength + currEditDistance);
                        if (!segmentIndex.containsLength(currentLength - currEditDistance - 1)) {
                            segmentIndex.addElementsWithLength(getValuesForLength(currentLength - currEditDistance - 1, columnIndex), currentLength - currEditDistance - 1);
                            if (possibleDependentsList.get(columnIndex).isEmpty()) {
                                segmentIndex.clearIndexStructure();
                            } else {
                                segmentIndex.indexByLength(currentLength - currEditDistance - 1);
                            }
                        }
                    }
                }
                if (measureTime) {
                    indexingTime += System.nanoTime() - indexStart;
                }
            }

            for (Integer columnIndex : currentReferencedColumns) {
                InvertedIndex segmentIndex = invertedIndexByColumn.get(columnIndex);
                segmentIndex.clear();
            }
        }
        return indexingTime;
    }

    private void writeColumnImpl(HashSet<Integer> needsDeduplication, Collection<SubstringableString> values, int columnIndex, int length) throws AlgorithmExecutionException {
        File tempFile = columnLengthFiles.get(columnIndex).get(length);
        if (tempFile == null) {
            tempFile = tempFileGenerator.getTemporaryFile();
            columnLengthFiles.get(columnIndex).put(length, tempFile);
        } else {
            needsDeduplication.add(columnIndex);
        }

        writeToFile(tempFile, values, true);
    }

    private void writeColumnSetToDisk(HashSet<Integer> needsDeduplication, HashMap<Integer, HashSet<SubstringableString>> columnValues, int columnIndex) throws AlgorithmExecutionException {
        System.out.println("Writing column " + columnIndex + " to disk");
        for (Map.Entry<Integer, HashSet<SubstringableString>> length2Values : columnValues.entrySet()) {
            writeColumnImpl(needsDeduplication, length2Values.getValue(), columnIndex, length2Values.getKey());
        }
    }

    private void writeColumnArrayToDisk(HashSet<Integer> needsDeduplication, HashMap<Integer, ArrayList<SubstringableString>> columnValues, int columnIndex) throws AlgorithmExecutionException {
        System.out.println("Writing column " + columnIndex + " to disk");
        for (Map.Entry<Integer, ArrayList<SubstringableString>> length2Values : columnValues.entrySet()) {
            writeColumnImpl(needsDeduplication, length2Values.getValue(), columnIndex, length2Values.getKey());
        }
    }

    private ArrayList<SubstringableString> getValuesForLength(int length, int columnIndex) throws AlgorithmExecutionException {
        ArrayList<SubstringableString> result = new ArrayList<>();
        try {
            for (Iterator<SubstringableString> it = getValueIteratorForLength(length, columnIndex, new HashSet<>()); it.hasNext(); ) {
                result.add(it.next());
            }
        } catch (IOException e) {
            e.printStackTrace();
            throw new AlgorithmExecutionException("Reading failed");
        }
        return result;
    }

    private Iterator<SubstringableString> getValueIteratorForLength(int length, int columnIndex, HashSet<Integer> currentReferencedColumns) throws IOException {
        if (currentReferencedColumns.contains(columnIndex)) {
            return invertedIndexByColumn.get(columnIndex).getElementsByLength(length).iterator();
        } else if (allValues.get(columnIndex).get(length) != null) {
            return allValues.get(columnIndex).get(length).iterator();
        } else {
            File tempFile = columnLengthFiles.get(columnIndex).get(length);
            if (tempFile == null) {
                return Collections.emptyIterator();
            } else {
                return new FileReader(tempFile);
            }
        }
    }

    private HashSet<Integer> getColumnSets(int numAllColumns, int ownIndex) {
        HashSet<Integer> set = new HashSet<>();
        for (int i = 0; i < numAllColumns; i++) {
            set.add(i);
        }
        set.remove(ownIndex);
        return set;
    }

    private ColumnPermutation getColumnPermutationByIndex(Integer index) {
        String[] columnId = indexToRelationColumn.get(index);
        return new ColumnPermutation(new ColumnIdentifier(columnId[0], columnId[1]));
    }

    private void writeToFile(File file, Collection<SubstringableString> values, boolean append) throws AlgorithmExecutionException {
        try {
            BufferedWriter writer = new BufferedWriter(new FileWriter(file, append));
            for (SubstringableString s : values) {
                writer.write(s.getUnderlyingChars());
                writer.write(System.lineSeparator());
            }
            writer.close();
        } catch (IOException e) {
            e.printStackTrace();
            throw new AlgorithmExecutionException("Temp file writing exception", e);
        }
    }

    private void writeTimingStatsToFile(ArrayList<TimingStats> timingStats, long indexingTime) throws AlgorithmExecutionException {
        try {
            BufferedWriter writer = new BufferedWriter(new FileWriter("target/timingStats.csv"));
            StringJoiner stringJoiner = new StringJoiner(",");
            stringJoiner.add("dependentColumn/referencedColumn");
            for (int i = 0; i < timingStats.size(); i++) {
                stringJoiner.add("validationTime_" + i);
            }
            for (int i = 0; i < timingStats.size(); i++) {
                stringJoiner.add("valueCount_" + i);
                stringJoiner.add("indexMatches_" + i);
            }
            writer.write(stringJoiner + System.lineSeparator());
            for (int i = 0; i < timingStats.size(); i++) {
                StringJoiner sj = new StringJoiner(",");
                sj.add(String.valueOf(i));
                for (int j = 0; j < timingStats.size(); j++) {
                    sj.add(String.valueOf(timingStats.get(i).validationTimePerColumn[j]));
                }
                for (int j = 0; j < timingStats.size(); j++) {
                    sj.add(String.valueOf(timingStats.get(i).validationValues[j]));
                    sj.add(String.valueOf(timingStats.get(i).indexMatches[j]));
                }
                writer.write(sj + System.lineSeparator());
            }
            writer.write("indexTime" + System.lineSeparator());
            writer.write(indexingTime + System.lineSeparator());

            writer.close();
        } catch (IOException e) {
            e.printStackTrace();
            throw new AlgorithmExecutionException("Temp file writing exception", e);
        }
    }

    private void writeErrorsToFile(HashMap<Integer, HashMap<Integer, LinkedList<InvertedSegmentIndex.NonDirectMatch>>> errors) throws AlgorithmExecutionException {
        try {
            BufferedWriter writer = new BufferedWriter(new FileWriter("target/nonDirectMatches.txt"));
            for (Map.Entry<Integer, HashMap<Integer, LinkedList<InvertedSegmentIndex.NonDirectMatch>>> dependant : errors.entrySet()) {
                for (Map.Entry<Integer, LinkedList<InvertedSegmentIndex.NonDirectMatch>> referenced : dependant.getValue().entrySet()) {
                    writer.write("Indirect Matches for sIND " + new InclusionDependency(getColumnPermutationByIndex(dependant.getKey()), getColumnPermutationByIndex(referenced.getKey())) + System.lineSeparator());
                    for (InvertedSegmentIndex.NonDirectMatch nonDirectMatch : referenced.getValue()) {
                        writer.write(nonDirectMatch.dependant + " : " + nonDirectMatch.referenced + System.lineSeparator());
                    }
                }
            }
            writer.close();
        } catch (IOException e) {
            e.printStackTrace();
            throw new AlgorithmExecutionException("Temp file writing exception", e);
        }
    }

    private int getEditDistanceFromIndex(int index) {
        if (index == 0) return 0;
        else if (index % 2 == 1) return (index + 1) / 2;
        else return index / -2;
    }

    private HashSet<Integer> getFittingColumns(HashSet<Integer> alreadyValidated, ArrayList<HashSet<Integer>> possibleDependentsList, ArrayList<Long> columnSizes) throws AlgorithmExecutionException {
        // FFD implementation to decide referenced columns for next iteration
        ArrayList<Utils.ColumnWithSize> columns = new ArrayList<>(columnSizes.size());
        for (int columnIndex = 0; columnIndex < columnSizes.size(); columnIndex++) {
            if (!alreadyValidated.contains(columnIndex)) {
                if (!possibleDependentsList.get(columnIndex).isEmpty()) {
                    columns.add(new Utils.ColumnWithSize(columnIndex, columnSizes.get(columnIndex)));
                } else {
                    alreadyValidated.add(columnIndex);
                }
            }
        }
        Collections.sort(columns);
        if (!columns.isEmpty() && columns.get(0).size > maxMemoryUsage) {
            throw new AlgorithmExecutionException("Cannot fit a column in memory!");
        }
        long currSum = 0L;
        HashSet<Integer> curr = new HashSet<>();
        for (Utils.ColumnWithSize entry : columns) {
            if (entry.size + currSum <= maxMemoryUsage) {
                currSum += entry.size;
                curr.add(entry.columnIndex);
                alreadyValidated.add(entry.columnIndex);
            }
        }
        return curr;
    }
}
