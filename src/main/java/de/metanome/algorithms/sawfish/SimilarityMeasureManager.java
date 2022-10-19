package de.metanome.algorithms.sawfish;

import de.metanome.algorithm_integration.AlgorithmConfigurationException;

public class SimilarityMeasureManager {
    private final boolean isNormalizedMode;
    private boolean hybridMode = false;
    private boolean tokenMode = false;
    private int absoluteEditDistance;
    private int[] normalizedEditDistance;
    private int[][] tokenThresholds;
    private float similarityThreshold;

    public SimilarityMeasureManager(int absoluteEditDistance, float similarityThreshold, boolean hybridMode, boolean tokenMode) throws AlgorithmConfigurationException {
        if (similarityThreshold == 0 && !hybridMode && !tokenMode) {
            this.isNormalizedMode = false;
            this.absoluteEditDistance = absoluteEditDistance;
        } else if (absoluteEditDistance == 0 && similarityThreshold != 0) {
            this.isNormalizedMode = true;
            if (tokenMode && !hybridMode) {
                this.tokenMode = true;
                this.similarityThreshold = similarityThreshold;
                tokenThresholds = new int[11][11];
                for (int i = 0; i < 11; i++) {
                    for (int j = 0; j < 11; j++) {
                        tokenThresholds[i][j] = (int) Math.ceil((similarityThreshold / (1 + similarityThreshold)) * (i + j));
                    }
                }
            } else if (!tokenMode) {
                this.similarityThreshold = similarityThreshold;
                this.hybridMode = hybridMode;
                normalizedEditDistance = new int[51];

                int maxEditDistance = (int) (50 * (1 - similarityThreshold));

                for (int i = 1; i <= 50; i++) {
                    int largestPossibleMatch = (int) (i / similarityThreshold);
                    int ed = largestPossibleMatch - i;
                    if (largestPossibleMatch >= 50) {
                        normalizedEditDistance[i] = maxEditDistance;
                    } else {
                        normalizedEditDistance[i] = hybridMode && ed == 0 ? 1 : ed;
                    }
                }
            } else {
                throw new AlgorithmConfigurationException("False configuration of similarity threshold");
            }
        } else {
            throw new AlgorithmConfigurationException("False configuration of similarity measure");
        }
    }

    public int getMaximumEditDistanceForLength(int length) {
        if (tokenMode) {
            return (int) Math.floor(length/similarityThreshold) - length;
        } else if (isNormalizedMode) {
            return normalizedEditDistance[length];
        } else {
            return absoluteEditDistance;
        }
    }

    public int getActualEditDistanceForLength(int length) {
        if (isNormalizedMode) {
            int returnValue = (int) (length * (1 - similarityThreshold));
            return returnValue == 0 && hybridMode ? 1 : returnValue;
        } else {
            return absoluteEditDistance;
        }
    }

    public int getMaximumEditDistance() {
        if (isNormalizedMode) {
            return normalizedEditDistance[50];
        } else {
            return absoluteEditDistance;
        }
    }

    public int getMaximumSegmentCountForLength(int length) {
        return getMaximumEditDistanceForLength(length) + 1;
    }

    public float getSimilarityThreshold() {
        return similarityThreshold;
    }

    public int getNumberOfPossibleSimilarLengths(int length) {
        if (tokenMode) {
            return (int) (Math.floor(length / similarityThreshold) - Math.ceil(length * similarityThreshold)) + 1;
        } else {
            if (isNormalizedMode) {
                return normalizedEditDistance[length] + getActualEditDistanceForLength(length) + 1;
            } else {
                return 2 * absoluteEditDistance + 1;
            }
        }
    }

    public int getTokenThreshold(int l1, int l2) {
        return tokenThresholds[l1][l2];
    }
}
