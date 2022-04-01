package de.metanome.algorithms.sawfish;

public class EditDistanceManager {
    private final boolean isNormalizedMode;
    private boolean hybridMode = false;
    private int absoluteEditDistance;
    private int[] normalizedEditDistance;
    private float similarityThreshold;

    public EditDistanceManager(int absoluteEditDistance) {
        isNormalizedMode = false;
        this.absoluteEditDistance = absoluteEditDistance;
    }

    public EditDistanceManager(float similarityThreshold) {
        isNormalizedMode = true;
        this.similarityThreshold = similarityThreshold;
        normalizedEditDistance = new int[51];

        int maxEditDistance = (int) (50 * (1 - similarityThreshold));

        for (int i = 1; i <= 50; i++) {
            int largestPossibleMatch = (int) (i / similarityThreshold);
            if (largestPossibleMatch >= 50) {
                normalizedEditDistance[i] = maxEditDistance;
            } else {
                normalizedEditDistance[i] = largestPossibleMatch - i;
            }
        }
    }

    public int getMaximumEditDistanceForLength(int length) {
        if (isNormalizedMode) {
            return normalizedEditDistance[length];
        } else {
            return absoluteEditDistance;
        }
    }

    public int getActualEditDistanceForLength(int length) {
        if (isNormalizedMode) {
            int returnValue = (int) (length * (1 - similarityThreshold));
            return returnValue == 0 && hybridMode ? 1: returnValue;
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

    public boolean isNormalizedMode() {
        return isNormalizedMode;
    }

    public void setHybridMode() {
        hybridMode = true;
        for (int i = 0; i <= 50; i++) {
            if (normalizedEditDistance[i] == 0) {
                normalizedEditDistance[i] = 1;
            } else {
                break;
            }
        }
    }

    public boolean isNullInitialized() {
        return isNormalizedMode ? similarityThreshold == 0f : absoluteEditDistance == 0;
    }
}
