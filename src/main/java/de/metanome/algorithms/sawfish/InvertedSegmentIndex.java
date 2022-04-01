package de.metanome.algorithms.sawfish;

import it.unimi.dsi.fastutil.ints.IntArrayList;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedList;

public class InvertedSegmentIndex {

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
    HashMap<Integer, ArrayList<HashMap<SubstringableString, IntArrayList>>> map;
    HashMap<Integer, ArrayList<SubstringableString>> length2Values;
    EditDistanceManager editDistanceManager;

    public InvertedSegmentIndex(EditDistanceManager ed) {
        editDistanceManager = ed;
        int editDistance = editDistanceManager.getMaximumEditDistance();
        map = new HashMap<>(2 * editDistance + 2, 1f);
        length2Values = new HashMap<>(2 * editDistance + 2, 1f);
    }

    public void addElement(SubstringableString element) {
        int length = element.length();
        length2Values.computeIfAbsent(length, l -> new ArrayList<>()).add(element);
    }

    public void addElementsWithLength(ArrayList<SubstringableString> elements, int length) {
        length2Values.put(length, elements);
    }

    public ArrayList<SubstringableString> getElementsByLength(int length) {
        ArrayList<SubstringableString> values = length2Values.get(length);
        return values == null ? new ArrayList<>(0) : values;
    }

    public void indexByLength(int length) {
        if (length <= 0) {
            return;
        }

        ArrayList<SubstringableString> values = length2Values.get(length);
        int editDistance = editDistanceManager.getMaximumEditDistanceForLength(length);

        if (values != null && !values.isEmpty()) {
            ArrayList<HashMap<SubstringableString, IntArrayList>> segmentList = new ArrayList<>(editDistance + 1);
            for (int i = 0; i < editDistance + 1; i++) {
                segmentList.add(new HashMap<>(values.size() + 1, 1f));
            }

            int[] startPositions = Utils.getStartPositions(length, editDistance + 1);
            for (int i = 0; i < values.size(); i++) {
                for (int j = 0; j < editDistance + 1; j++) {
                    if (startPositions[j] != startPositions[j + 1]) {
                        segmentList.get(j).computeIfAbsent(values.get(i).substring(startPositions[j], startPositions[j + 1]), s -> new IntArrayList(2)).add(i);
                    }
                }
            }
            map.put(length, segmentList);
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

    public SimilarMatches getPossibleSimilarStringsForSubstrings(ArrayList<ArrayList<SubstringableString>> substrings, int queryLength, int segmentIndex, HashSet<Integer> alreadyValidatedSet) {
        LinkedList<Match> result = new LinkedList<>();
        int editDistance = editDistanceManager.getMaximumEditDistanceForLength(queryLength);
        ArrayList<HashMap<SubstringableString, IntArrayList>> segmentList = map.get(queryLength);
        if (segmentList != null) {
            // for each segment position
            for (; segmentIndex < editDistance + 1; segmentIndex++) {
                HashMap<SubstringableString, IntArrayList> segment2Indices = segmentList.get(segmentIndex);
                // for each generated substring for that segment position, find a matching segment and save match
                for (SubstringableString substring : substrings.get(segmentIndex)) {
                    IntArrayList matches = segment2Indices.get(substring);
                    if (matches != null) {
                        for (int i : matches) {
                            if (!alreadyValidatedSet.contains(i)) {
                                result.add(new Match(i, substring.getStartPosition()));
                                alreadyValidatedSet.add(i);
                            }
                        }
                    }
                }
                if (!result.isEmpty()) {
                    return new SimilarMatches(result, segmentIndex, substrings.get(segmentIndex).get(0).length());
                }
            }
        }
        return new SimilarMatches(result, segmentIndex, 0);
    }
}
