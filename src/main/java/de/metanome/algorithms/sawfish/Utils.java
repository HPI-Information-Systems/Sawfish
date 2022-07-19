package de.metanome.algorithms.sawfish;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.regex.Pattern;

public class Utils {
    static class ColumnWithSize implements Comparable<ColumnWithSize> {
        public long size;
        public int columnIndex;

        public ColumnWithSize(int columnIndex, long size) {
            this.columnIndex = columnIndex;
            this.size = size;
        }

        @Override
        public int compareTo(ColumnWithSize columnWithSize) {
            return (int) (columnWithSize.size - this.size);
        }
    }

    static class SubstringInformation {
        public byte minPos;
        public byte maxPos;
        public byte segmentLength;

        public SubstringInformation(byte minPos, byte maxPos, byte segmentLength) {
            this.minPos = minPos;
            this.maxPos = maxPos;
            this.segmentLength = segmentLength;
        }
    }

    // inputLength -> queryLength -> segment -> substringInformation
    public static HashMap<Integer, HashMap<Integer, ArrayList<Utils.SubstringInformation>>> substringInfos = new HashMap<>();
    public static int[][] editDistanceBuffer;

    public static Pattern delimiterPattern = Pattern.compile("\\s+");

    public static int getElementLength(String string, boolean tokenMode) {
        if (tokenMode) {
            HashSet<String> set = new HashSet<>(2);
            set.addAll(Arrays.asList(delimiterPattern.split(string)));
            return set.size();
        } else {
            return string.length();
        }
    }

    static public int[] getStartPositions(int length, int segmentCount) {
        int[] result = new int[segmentCount + 1];
        int longSegments = length % segmentCount;
        int shortSegments = segmentCount - longSegments;
        int segmentLength = length / segmentCount;
        for (int i = 0; i < shortSegments; i++) {
            result[i] = i * segmentLength;
        }
        int offset = shortSegments * segmentLength;
        segmentLength++;
        for (int i = 0; i < longSegments; i++) {
            result[i + shortSegments] = offset + i * segmentLength;
        }
        result[segmentCount] = length;
        return result;
    }

    static public int getStartPositionFromSegmentIndex(int segmentIndex, int stringLength, int segmentCount) {
        int longSegments = stringLength % segmentCount;
        int shortSegments = segmentCount - longSegments;
        int segmentLength = stringLength / segmentCount;
        int longSegmentOffset = segmentIndex - shortSegments;
        if (longSegmentOffset > 0) {
            return segmentIndex * segmentLength + longSegmentOffset;
        }
        return segmentIndex * segmentLength;
    }

    static public ArrayList<ArrayList<SubstringableString>> generateSubstrings(SubstringableString input, ArrayList<SubstringInformation> substringInformation, int segmentCount, int queriedLength) {
        ArrayList<ArrayList<SubstringableString>> result = new ArrayList<>(segmentCount);
        if (segmentCount > queriedLength) {
            ArrayList<SubstringableString> allCharacters = new ArrayList<>(input.length());
            for (int i = 0; i < input.length(); i++) {
                allCharacters.add(input.substring(i, i + 1));
            }
            for (int i = 0; i < segmentCount - queriedLength; i++) {
                result.add(new ArrayList<>(0));
            }
            for (int i = segmentCount - queriedLength; i < segmentCount; i++) {
                result.add(allCharacters);
            }
        } else {
            for (SubstringInformation s : substringInformation) {
                ArrayList<SubstringableString> curr = new ArrayList<>();
                for (int j = s.minPos; j <= s.maxPos; j++) {
                    curr.add(input.substring(j - 1, j - 1 + s.segmentLength));
                }
                result.add(curr);
            }
        }
        return result;
    }

    static public ArrayList<SubstringInformation> generateSubstringInformation(int segmentCount, int inputLength, int queriedLength) {
        if (segmentCount > queriedLength) return new ArrayList<>(0);

        ArrayList<SubstringInformation> result = new ArrayList<>(segmentCount);
        int lengthDifference = inputLength - queriedLength;

        int startPosition = 1;
        int segmentLength = queriedLength / segmentCount;
        int shortSegments = segmentCount - (queriedLength % segmentCount);
        for (int i = 1; i <= segmentCount; i++) {
            int minL = startPosition - i + 1;
            int minR = startPosition + lengthDifference - (segmentCount - 1 + 1 - i);
            int minPos = Math.max(1, Math.max(minL, minR));

            int maxL = startPosition + i - 1;
            int maxR = startPosition + lengthDifference + (segmentCount - 1 + 1 - i);
            int maxPos = Math.min(inputLength - segmentLength + 1, Math.min(maxL, maxR));

            result.add(new SubstringInformation((byte) minPos, (byte) maxPos, (byte) segmentLength));

            startPosition += segmentLength;

            if (i == shortSegments)
                segmentLength++;
        }
        return result;
    }

    static public ArrayList<ArrayList<SubstringableString>> generateSubstrings(SubstringableString input, int segmentCount, int queriedLength) {
        ArrayList<ArrayList<SubstringableString>> result = new ArrayList<>(segmentCount);
        if (segmentCount > queriedLength) {
            ArrayList<SubstringableString> allCharacters = new ArrayList<>(input.length());
            for (int i = 0; i < input.length(); i++) {
                allCharacters.add(input.substring(i, i + 1));
            }
            for (int i = 0; i < segmentCount - queriedLength; i++) {
                result.add(new ArrayList<>(0));
            }
            for (int i = segmentCount - queriedLength; i < segmentCount; i++) {
                result.add(allCharacters);
            }
        } else {
            int lengthDifference = input.length() - queriedLength;

            int startPosition = 1;
            int segmentLength = queriedLength / segmentCount;
            int shortSegments = segmentCount - (queriedLength % segmentCount);
            for (int i = 1; i <= segmentCount; i++) {
                ArrayList<SubstringableString> curr = new ArrayList<>();

                int minL = startPosition - i + 1;
                int minR = startPosition + lengthDifference - (segmentCount - 1 + 1 - i);
                int minPos = Math.max(1, Math.max(minL, minR));

                int maxL = startPosition + i - 1;
                int maxR = startPosition + lengthDifference + (segmentCount - 1 + 1 - i);
                int maxPos = Math.min(input.length() - segmentLength + 1, Math.min(maxL, maxR));

                for (int j = minPos; j <= maxPos; j++) {
                    curr.add(input.substring(j - 1, j - 1 + segmentLength));
                }

                startPosition += segmentLength;

                if (i == shortSegments)
                    segmentLength++;

                result.add(curr);
            }
        }
        return result;
    }


    // Inspired by the EditDistanceClusterer (https://github.com/lispc/EditDistanceClusterer) - Copyright (c) [2015] [Zhuo Zhang]
    static public boolean isWithinEditDistance(SubstringableString src, SubstringableString dst, int srcMatchPos, int dstMatchPos, int len, int threshold,
                                               int[][] distanceBuffer, int[] editDistance) {
        int srcRightLen = src.length() - srcMatchPos - len;
        int dstRightLen = dst.length() - dstMatchPos - len;
        int leftThreshold = threshold - Math.abs(srcRightLen - dstRightLen);
        int leftDistance = calculateEditDistanceWithThreshold(src, 0, srcMatchPos,
                dst, 0, dstMatchPos,
                leftThreshold, distanceBuffer);
        if (leftDistance > leftThreshold) {
            return false;
        }
        int rightThreshold = threshold - leftDistance;
        int rightDistance = calculateEditDistanceWithThreshold(
                src, srcMatchPos + len, src.length() - srcMatchPos - len,
                dst, dstMatchPos + len, dst.length() - dstMatchPos - len,
                rightThreshold, distanceBuffer);
        editDistance[0] = leftDistance + rightDistance;
        return rightDistance <= rightThreshold;
    }

    // Inspired by the EditDistanceClusterer (https://github.com/lispc/EditDistanceClusterer) - Copyright (c) [2015] [Zhuo Zhang]
    static public int calculateEditDistanceWithThreshold(SubstringableString s1, int start1, int l1,
                                                         SubstringableString s2, int start2, int l2, int threshold, int[][] distanceBuffer) {
        if (threshold < 0) {
            return 0;
        }
        if (threshold == 0) {
            SubstringableString sub1 = s1.substring(start1, start1 + l1);
            SubstringableString sub2 = s2.substring(start2, start2 + l2);
            return sub1.equals(sub2) ? 0 : 1;
        }
        if (l1 == 0) {
            return l2;
        }
        if (l2 == 0) {
            return l1;
        }
        char[] s1_chars = s1.getUnderlyingChars();
        char[] s2_chars = s2.getUnderlyingChars();
        for (int j = 1; j <= l1; j++) {
            int start = Math.max(j - threshold, 1);
            int end = Math.min(l2, j + threshold);
            if (j - threshold - 1 >= 1) {
                distanceBuffer[j - threshold - 1][j] = threshold + 1;
            }

            for (int i = start; i <= end; i++) {
                if (s1_chars[start1 + j - 1] == s2_chars[start2 + i - 1]) {
                    distanceBuffer[i][j] = distanceBuffer[i - 1][j - 1];
                } else {
                    distanceBuffer[i][j] = Math.min(distanceBuffer[i - 1][j - 1] + 1,
                            Math.min(distanceBuffer[i - 1][j] + 1, distanceBuffer[i][j - 1] + 1));
                }
            }
            if (end < l2)
                distanceBuffer[end + 1][j] = threshold + 1;
            boolean earlyTerminateFlag = true;
            for (int i = start; i <= end; i++) {
                if (distanceBuffer[i][j] <= threshold) {
                    earlyTerminateFlag = false;
                    break;
                }
            }
            if (earlyTerminateFlag)
                return threshold + 1;
        }
        return distanceBuffer[l2][l1];
    }
}
