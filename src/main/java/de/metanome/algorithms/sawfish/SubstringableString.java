package de.metanome.algorithms.sawfish;

public class SubstringableString {
    private final char[] value;
    private final byte offset;
    private final byte length;
    private int hash = 0;

    public SubstringableString(char[] value, byte offset, byte length) {
        this.value = value;
        this.offset = offset;
        this.length = length;
    }

    public SubstringableString(char[] value) {
        this.value = value;
        this.offset = 0;
        this.length = (byte) this.value.length;
    }

    public SubstringableString(String string) {
        this.value = string.toCharArray();
        this.offset = 0;
        this.length = (byte) this.value.length;
    }

    public SubstringableString(char[] value, int offset, int length) {
        this.value = value;
        this.offset = (byte) offset;
        this.length = (byte) length;
    }

    public int length() {
        return length;
    }

    public int getStartPosition() {
        return offset;
    }

    public char[] getUnderlyingChars() {
        return value;
    }

    public String toString() {
        return new String(value, offset, length);
    }

    public SubstringableString substring(int startPosition, int endPosition) {
        if (startPosition == 0 && endPosition - startPosition == length) return this;
        return new SubstringableString(this.value, offset + startPosition, endPosition - startPosition);
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) {
            return true;
        } else {
            if (o instanceof SubstringableString) {
                SubstringableString other = (SubstringableString) o;
                if (this.length == other.length) {
                    for (int i = 0; i < length; i++) {
                        if (this.value[this.offset + i] != other.value[other.offset + i]) {
                            return false;
                        }
                    }
                    return true;
                }
            }
            return false;
        }
    }

    @Override
    public int hashCode() {
        if (this.hash == 0 && this.length > 0) {
            for (int i = 0; i < this.length; i++) {
                this.hash = 31 * this.hash + this.value[offset + i];
            }
        }

        return hash;
    }
}
