package de.metanome.algorithms.sawfish;

import java.io.*;
import java.util.Arrays;
import java.util.Iterator;

public class FileReader implements Iterator<SubstringableString> {
    private final BufferedReader reader;
    private final char[] buffer = new char[1];
    private final char[] nextStringBuffer = new char[50];
    private int index = 0;
    private SubstringableString nextString = null;

    public FileReader(File file) throws IOException {
        reader = new BufferedReader(new InputStreamReader(new FileInputStream(file)));
    }

    private SubstringableString getNextString() {
        try {
            int status = reader.read(buffer);
            while (status != -1 && buffer[0] != '\n') {
                nextStringBuffer[index] = buffer[0];
                index++;
                status = reader.read(buffer);
            }
        } catch (IOException e) {
            return null;
        }
        if (index == 0) {
            return null;
        }
        char[] newValue = Arrays.copyOf(nextStringBuffer, index);
        index = 0;
        return new SubstringableString(newValue);
    }


    @Override
    public boolean hasNext() {
        if (nextString == null) {
            nextString = getNextString();
        }
        return nextString != null;
    }

    @Override
    public SubstringableString next() {
        if (nextString != null) {
            SubstringableString returnValue = nextString;
            nextString = null;
            return returnValue;
        } else {
            return getNextString();
        }
    }

    public boolean hasMoreValues() {
        return false;
    }
}
