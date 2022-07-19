package de.metanome.algorithms.sawfish;

import it.unimi.dsi.fastutil.ints.IntArrayList;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedList;

public abstract class InvertedIndex {

    static class SimilarMatches {
        public LinkedList<Match> matches;
        public int segmentIndex;
        public int lengthOfMatches;

        public SimilarMatches(LinkedList<Match> matches, int segmentIndex, int lengthOfMatches) {
            this.matches = matches;
            this.segmentIndex = segmentIndex;
            this.lengthOfMatches = lengthOfMatches;
        }
    }

    static class Match {
        public int matchedId;
        public int startOfMatch;

        public Match(int matchedId, int startOfMatch) {
            this.matchedId = matchedId;
            this.startOfMatch = startOfMatch;
        }
    }

    static class NonDirectMatch {
        public String dependant;
        public String referenced;

        public NonDirectMatch(String dependant, String referenced) {
            this.dependant = dependant;
            this.referenced = referenced;
        }
    }

    // length -> i-th segment -> segment -> elementId
    protected HashMap<Integer, ArrayList<HashMap<SubstringableString, IntArrayList>>> map;
    protected HashMap<Integer, ArrayList<SubstringableString>> length2Values;
    protected SimilarityMeasureManager similarityMeasureManager;

    public void addElementsWithLength(ArrayList<SubstringableString> elements, int length) {
        length2Values.put(length, elements);
    }

    public ArrayList<SubstringableString> getElementsByLength(int length) {
        ArrayList<SubstringableString> values = length2Values.get(length);
        return values == null ? new ArrayList<>(0) : values;
    }

    abstract void indexByLengthImpl(ArrayList<SubstringableString> values, int length);

    public void indexByLength(int length) {
        if (length <= 0) {
            return;
        }

        ArrayList<SubstringableString> values = length2Values.get(length);
        if (values != null && !values.isEmpty()) {
            indexByLengthImpl(values, length);
        }
    }

    public void removeLengthFromIndex(int length) {
        map.remove(length);
        length2Values.remove(length);
    }

    public void clearIndexStructure() {
        map.clear();
    }

    public void clear() {
        map.clear();
        length2Values.clear();
    }

    public boolean containsLength(int length) {
        return map.containsKey(length);
    }

    public abstract boolean existsSimilarReferencedValueForLength(SubstringableString searchString, int queryLength, int dependentColumnIndex, int referencedColumnIndex, HashMap<Integer, HashMap<Integer, LinkedList<NonDirectMatch>>> errors, TimingStats t);
}
