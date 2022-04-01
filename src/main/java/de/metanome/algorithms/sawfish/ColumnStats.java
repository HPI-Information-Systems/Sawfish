package de.metanome.algorithms.sawfish;

public class ColumnStats {
    public int shortestLength;
    public int longestLength;
    public boolean canBeInteger;
    public boolean canBeFloat;
    public boolean hasShortValue; // value that is shorter or equal to edit distance

    public ColumnStats() {
        this.shortestLength = Integer.MAX_VALUE;
        this.longestLength = 0;
        this.canBeInteger = true;
        this.canBeFloat = true;
        this.hasShortValue = false;
    }
}
