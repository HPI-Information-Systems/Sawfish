package de.metanome.algorithms.sawfish;

public class TimingStats {
    public long[] validationTimePerColumn;
    public long[] indexMatches;
    public long[] validationValues;

    public TimingStats(int size) {
        validationTimePerColumn = new long[size];
        indexMatches = new long[size];
        validationValues = new long[size];
    }
}
