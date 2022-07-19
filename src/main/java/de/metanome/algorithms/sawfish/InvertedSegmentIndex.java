package de.metanome.algorithms.sawfish;

import it.unimi.dsi.fastutil.ints.IntArrayList;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedList;

public class InvertedSegmentIndex extends InvertedIndex {
    public InvertedSegmentIndex(SimilarityMeasureManager ed) {
        similarityMeasureManager = ed;
        int editDistance = similarityMeasureManager.getMaximumEditDistance();
        map = new HashMap<>(2 * editDistance + 2, 1f);
        length2Values = new HashMap<>(2 * editDistance + 2, 1f);
    }

    @Override
    void indexByLengthImpl(ArrayList<SubstringableString> values, int length) {
        int editDistance = similarityMeasureManager.getMaximumEditDistanceForLength(length);

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

    @Override
    public boolean existsSimilarReferencedValueForLength(SubstringableString searchString, int queryLength, int dependentColumnIndex, int referencedColumnIndex, HashMap<Integer, HashMap<Integer, LinkedList<NonDirectMatch>>> errors, TimingStats t) {
        HashSet<Integer> alreadyValidated = new HashSet<>();
        int[] editDistanceReturn = new int[1];
        int segmentCount = similarityMeasureManager.getMaximumSegmentCountForLength(queryLength);
        ArrayList<Utils.SubstringInformation> subInfo = Utils.substringInfos.computeIfAbsent(searchString.length(), i -> new HashMap<>()).computeIfAbsent(queryLength, qL -> Utils.generateSubstringInformation(segmentCount, searchString.length(), queryLength));
        ArrayList<ArrayList<SubstringableString>> substrings = Utils.generateSubstrings(searchString, subInfo, segmentCount, queryLength);
        for (int segmentIndex = 0; segmentIndex < segmentCount; segmentIndex++) {
            InvertedSegmentIndex.SimilarMatches similarMatches;
            similarMatches = getPossibleSimilarStringsForSubstrings(substrings, queryLength, segmentIndex, alreadyValidated);
            segmentIndex = similarMatches.segmentIndex;
            if (t != null) {
                t.indexMatches[dependentColumnIndex] += similarMatches.matches.size();
            }

            // if no possible similar strings are found, the candidate cannot be referenced and needs to be removed
            if (!similarMatches.matches.isEmpty()) {
                // validate each match as long as string is not already verified
                for (InvertedSegmentIndex.Match match : similarMatches.matches) {
                    SubstringableString matchedString = length2Values.get(queryLength).get(match.matchedId);
                    int segmentMatchPos = Utils.getStartPositionFromSegmentIndex(segmentIndex, matchedString.length(), segmentCount);
                    int actualEditDistance = similarityMeasureManager.getActualEditDistanceForLength(Math.max(queryLength, searchString.length()));
                    boolean candidateVerified = Utils.isWithinEditDistance(searchString, matchedString, match.startOfMatch, segmentMatchPos, similarMatches.lengthOfMatches, actualEditDistance, Utils.editDistanceBuffer, editDistanceReturn);

                    if (candidateVerified) {
                        if (errors != null && editDistanceReturn[0] > 0) {
                            errors.computeIfAbsent(dependentColumnIndex, k -> new HashMap<>()).computeIfAbsent(referencedColumnIndex, k -> new LinkedList<>()).add(new InvertedSegmentIndex.NonDirectMatch(searchString.toString(), matchedString.toString()));
                        }
                        return true;
                    }
                }
            }
        }
        return false;
    }

    public ArrayList<SubstringableString> getPossibleSimilarStrings(SubstringableString queryString) {
        int maxOuterEditDistance = similarityMeasureManager.getMaximumEditDistanceForLength(queryString.length());
        ArrayList<SubstringableString> result = new ArrayList<>();
        // for each possible edit distance
        for (int i = -maxOuterEditDistance; i <= maxOuterEditDistance; i++) {
            int queryLength = queryString.length() + i;
            int innerEditDistance = similarityMeasureManager.getMaximumEditDistanceForLength(queryLength);
            ArrayList<ArrayList<SubstringableString>> substrings = Utils.generateSubstrings(queryString, innerEditDistance + 1, queryLength);

            HashSet<Integer> alreadyKnown = new HashSet<>();
            for (int segmentIndex = 0; segmentIndex < innerEditDistance + 1; segmentIndex++) {
                for (Match m : getPossibleSimilarStringsForSubstrings(substrings, queryString.length() + i, segmentIndex, alreadyKnown).matches) {
                    result.add(length2Values.get(queryString.length() + i).get(m.matchedId));
                }
            }
        }
        return result;
    }

    public SimilarMatches getPossibleSimilarStringsForSubstrings(ArrayList<ArrayList<SubstringableString>> substrings, int queryLength, int segmentIndex, HashSet<Integer> alreadyValidatedSet) {
        LinkedList<Match> result = new LinkedList<>();
        int editDistance = similarityMeasureManager.getMaximumEditDistanceForLength(queryLength);
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
