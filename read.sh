#!/bin/bash

INPUT_FILE="input.txt"
OUTPUT_FILE="output.json"

# Start JSON array
echo "[" > "$OUTPUT_FILE"

# Process rows by splitting on </tr>
awk -v RS="</tr>" '
/<tr/ {
    # Split columns using </td>
    n = split($0, cols, "</td>")

    if (n >= 3) {
        # Extract Italian (2nd column)
        match(cols[2], />[^<]*/)
        italian = substr(cols[2], RSTART+1, RLENGTH-1)

        # Extract English (3rd column)
        match(cols[3], />[^<]*/)
        english = substr(cols[3], RSTART+1, RLENGTH-1)

        # Trim whitespace
        gsub(/^[ \t]+|[ \t]+$/, "", italian)
        gsub(/^[ \t]+|[ \t]+$/, "", english)

        # Escape quotes for JSON safety
        gsub(/"/, "\\\"", italian)
        gsub(/"/, "\\\"", english)

        # Only print valid rows
        if (italian != "" && english != "") {
            printf "  {\"italian\": \"%s\", \"english\": \"%s\"},\n", italian, english
        }
    }
}
' "$INPUT_FILE" >> "$OUTPUT_FILE"

# Remove trailing comma (macOS + Linux compatible)
sed -i '' -e '$ s/,$//' "$OUTPUT_FILE" 2>/dev/null || sed -i '$ s/,$//' "$OUTPUT_FILE"

# Close JSON array
echo "]" >> "$OUTPUT_FILE"

echo "✅ Done. Output written to $OUTPUT_FILE"