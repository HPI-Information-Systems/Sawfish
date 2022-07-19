package de.metanome.algorithms.sawfish;

import java.util.HashSet;
import java.util.regex.Matcher;

public class TokenizedString extends SubstringableString {
    private final SubstringableString[] tokens;

    public TokenizedString(char[] value) {
        super(value);
        Matcher m = Utils.delimiterPattern.matcher(this);
        HashSet<SubstringableString> tokens = new HashSet<>(10, 1f);
        int lastLoc = 0;
        while (m.find()) {
            tokens.add(this.substring(lastLoc, m.start()));
            lastLoc = m.end();
        }
        tokens.add(this.substring(lastLoc, value.length));
        this.tokens = tokens.toArray(new SubstringableString[0]);
    }

    public TokenizedString(char[] value, SubstringableString[] tokens) {
        super(value);
        this.tokens = tokens;
    }

    @Override
    public SubstringableString[] getTokens() {
        return tokens;
    }

    @Override
    public int elLength() {
        return tokens.length;
    }
}
