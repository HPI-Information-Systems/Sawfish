package de.metanome.algorithms.sawfish;

import it.unimi.dsi.fastutil.ints.Int2ByteOpenHashMap;
import it.unimi.dsi.fastutil.ints.IntArrayList;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedList;

public class InvertedTokenIndex extends InvertedIndex {
    public InvertedTokenIndex(SimilarityMeasureManager ed) {
        similarityMeasureManager = ed;
        int gap = similarityMeasureManager.getNumberOfPossibleSimilarLengths(10);
        map = new HashMap<>(gap + 1, 1f);
        length2Values = new HashMap<>(gap + 1, 1f);
    }

    @Override
    void indexByLengthImpl(ArrayList<SubstringableString> values, int length) {
        HashMap<SubstringableString, IntArrayList> tokenIndex = new HashMap<>();
        for (int i = 0; i < values.size(); i++) {
            for (SubstringableString s : values.get(i).getTokens()) {
                tokenIndex.computeIfAbsent(s, a -> new IntArrayList(2)).add(i);
            }
        }
        ArrayList<HashMap<SubstringableString, IntArrayList>> list = new ArrayList<>(1);
        list.add(tokenIndex);
        map.put(length, list);
    }

    @Override
    public boolean existsSimilarReferencedValueForLength(SubstringableString searchString, int queryLength, int dependentColumnIndex, int referencedColumnIndex, HashMap<Integer, HashMap<Integer, LinkedList<NonDirectMatch>>> errors, TimingStats t) {
        Int2ByteOpenHashMap id2Count = new Int2ByteOpenHashMap();
        SubstringableString[] tokens = searchString.getTokens();
        int threshold = similarityMeasureManager.getTokenThreshold(tokens.length, queryLength);
        if (threshold > queryLength) return false;

        for (SubstringableString s : tokens) {
            ArrayList<HashMap<SubstringableString, IntArrayList>> index = map.get(queryLength);
            if (index != null) {
                IntArrayList ids = index.get(0).get(s);
                if (ids != null) {
                    if (t != null) {
                        t.indexMatches[dependentColumnIndex] += ids.size();
                    }
                    for (int i : ids) {
                        byte oldCount = id2Count.get(i);
                        oldCount++;
                        if (oldCount == threshold) {
                            return true;
                        } else {
                            id2Count.put(i, oldCount);
                        }
                    }
                }
            }
        }
        return false;
    }
}
