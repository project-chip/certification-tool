#!/usr/bin/env bash
# pics_to_xml.sh — Convert PICS log data to XML PICS files.
#
# Accepts two input formats:
#   1. Python dict log:  PICSItem(number='KEY', enabled=True/False)
#   2. KEY=0/1 lines (raw or inside an "echo '...'" block)
#
# Usage:
#   ./pics_to_xml.sh <input_file> [output_dir]
#   ./pics_to_xml.sh --text "MCORE.S=1\nMCORE.C=0" [-o output_dir]
#
# Options:
#   --text "..."   Inline PICS text instead of a file (use \n to separate lines)
#   -o <dir>       Output directory (default: alongside input file, or cwd for --text)
#
# One XML file is produced per cluster prefix (MCORE, JFADMIN, JFDS, ...).

usage() {
    echo "Usage: $0 <input_file> [output_dir]"
    echo "       $0 --text \"KEY=0/1 ...\" [-o output_dir]"
    exit 1
}

[ $# -eq 0 ] && usage

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
TEXT_MODE=0
INLINE_TEXT=""
INPUT_FILE=""
OUTPUT_DIR=""

while [ $# -gt 0 ]; do
    case "$1" in
        --text)
            [ -z "$2" ] && { echo "ERROR: --text requires a value" >&2; exit 1; }
            TEXT_MODE=1
            INLINE_TEXT="$2"
            shift 2
            ;;
        -o|--output-dir)
            [ -z "$2" ] && { echo "ERROR: -o requires a value" >&2; exit 1; }
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -*)
            echo "ERROR: Unknown option: $1" >&2; usage
            ;;
        *)
            if [ -z "$INPUT_FILE" ]; then
                INPUT_FILE="$1"
            elif [ -z "$OUTPUT_DIR" ]; then
                OUTPUT_DIR="$1"   # positional second arg kept for back-compat
            else
                echo "ERROR: Unexpected argument: $1" >&2; usage
            fi
            shift
            ;;
    esac
done

if [ "$TEXT_MODE" -eq 0 ]; then
    [ -z "$INPUT_FILE" ] && usage
    [ ! -f "$INPUT_FILE" ] && { echo "ERROR: File not found: $INPUT_FILE" >&2; exit 1; }
    OUTPUT_DIR="${OUTPUT_DIR:-$(dirname "$INPUT_FILE")}"
else
    [ -n "$INPUT_FILE" ] && { echo "ERROR: --text and a file path are mutually exclusive" >&2; exit 1; }
    OUTPUT_DIR="${OUTPUT_DIR:-$(pwd)}"
fi

mkdir -p "$OUTPUT_DIR"

TMPFILE=$(mktemp)
SRCFILE=$(mktemp)
trap 'rm -f "$TMPFILE" "$SRCFILE"' EXIT

# ---------------------------------------------------------------------------
# Populate SRCFILE from either --text or the input file
# ---------------------------------------------------------------------------
if [ "$TEXT_MODE" -eq 1 ]; then
    # Interpret \n escape sequences so the user can pass multi-line text inline
    printf '%b' "$INLINE_TEXT" > "$SRCFILE"
else
    cp "$INPUT_FILE" "$SRCFILE"
fi

# ---------------------------------------------------------------------------
# Parse into TMPFILE: one line per item  KEY=true|false
# ---------------------------------------------------------------------------
if grep -q "PICSItem(" "$SRCFILE"; then
    # Python-dict format: PICSItem(number='KEY', enabled=True/False)
    perl -nle '
        while (/PICSItem\(number='"'"'([^'"'"']+)'"'"',\s*enabled=(True|False)\)/g) {
            $sup = lc($2) eq "true" ? "true" : "false";
            print "$1=$sup";
        }
    ' "$SRCFILE" > "$TMPFILE"
else
    # KEY=0/1 format
    grep -E '^[A-Za-z0-9_.]+=[01]$' "$SRCFILE" \
        | awk -F= '{print $1 "=" ($2=="1" ? "true" : "false")}' \
        > "$TMPFILE"
fi

[ -s "$TMPFILE" ] || { echo "ERROR: No PICS items found in input." >&2; exit 1; }

# ---------------------------------------------------------------------------
# Use awk to build each cluster's XML
# ---------------------------------------------------------------------------
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
PREFIXES=$(awk -F= '{n=split($1,a,"."); print a[1]}' "$TMPFILE" | sort -u)

WRITTEN=0
for PREFIX in $PREFIXES; do
    OUTFILE="${OUTPUT_DIR}/${PREFIX}.xml"

    awk -v prefix="$PREFIX" -v ts="$TIMESTAMP" -v outfile="$OUTFILE" '
    BEGIN {
        FS = "="
        n = 0
    }

    # Categorise a key
    function cat(key,    parts, np) {
        np = split(key, parts, ".")
        # usage: exactly PREFIX.S or PREFIX.C
        if (np == 2 && (parts[2] == "S" || parts[2] == "C"))
            return "usage"
        # attributes: third segment starts with A and hex digit
        if (np >= 3 && parts[2] ~ /^[SC]$/ && parts[3] ~ /^[Aa][0-9a-fA-F]/)
            return "attributes"
        # events: third segment starts with E and hex digit
        if (np >= 3 && parts[2] ~ /^[SC]$/ && parts[3] ~ /^[Ee][0-9a-fA-F]/)
            return "events"
        # commandsGenerated: third segment starts with C, last segment is Tx
        if (np >= 4 && parts[2] ~ /^[SC]$/ && parts[3] ~ /^C/ && parts[np] == "Tx")
            return "commandsGenerated"
        # commandsReceived: third segment starts with C, last segment is Rsp
        if (np >= 4 && parts[2] ~ /^[SC]$/ && parts[3] ~ /^C/ && parts[np] == "Rsp")
            return "commandsReceived"
        # features: third segment starts with F and hex digit
        if (np >= 3 && parts[2] ~ /^[SC]$/ && parts[3] ~ /^[Ff][0-9a-fA-F]/)
            return "features"
        return "manually"
    }

    # side of a key: S, C, or "" for items with no clear side
    function side(key,    parts, np) {
        np = split(key, parts, ".")
        if (np >= 2 && (parts[2] == "S" || parts[2] == "C"))
            return parts[2]
        return ""
    }

    /^[A-Za-z0-9_.]+=(true|false)$/ {
        key = $1; sup = $2
        # only collect items for our prefix
        split(key, p, ".")
        if (p[1] != prefix) next
        keys[n] = key
        sups[n] = sup
        n++
    }

    END {
        t  = "\t"
        tt = "\t\t"
        ttt= "\t\t\t"
        tttt="\t\t\t\t"

        print "<?xml version=\"1.0\" ?>"
        print "<!--"
        print "Autogenerated xml file"
        print "Generated date:" ts
        print "Cluster Name -" prefix
        print "-->"
        print "<clusterPICS xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:noNamespaceSchemaLocation=\"Generic-PICS-XML-Schema.xsd\">"
        print t "<name>" prefix "</name>"
        print t "<clusterId> </clusterId>"
        print t "<picsRoot> </picsRoot>"
        print t "<pixit/>"

        # --- usage ---
        has_usage = 0
        for (i = 0; i < n; i++) if (cat(keys[i]) == "usage") { has_usage = 1; break }
        if (has_usage) {
            print t "<usage>"
            for (i = 0; i < n; i++) {
                if (cat(keys[i]) != "usage") continue
                print tt "<picsItem>"
                print ttt "<itemNumber>" keys[i] "</itemNumber>"
                print ttt "<feature/>"
                print ttt "<reference/>"
                print ttt "<status>O</status>"
                print ttt "<support>" sups[i] "</support>"
                print tt "</picsItem>"
            }
            print t "</usage>"
        } else {
            print t "<usage/>"
        }

        # --- clusterSide ---
        for (si = 0; si < 2; si++) {
            sl = (si == 0) ? "S" : "C"
            st = (si == 0) ? "Server" : "Client"
            print t "<clusterSide type=\"" st "\">"

            sections[0] = "attributes"
            sections[1] = "events"
            sections[2] = "commandsGenerated"
            sections[3] = "commandsReceived"
            sections[4] = "features"
            sections[5] = "manually"

            for (s = 0; s < 6; s++) {
                sec = sections[s]
                has_items = 0
                for (i = 0; i < n; i++) {
                    if (cat(keys[i]) != sec) continue
                    if (side(keys[i]) != sl) continue
                    has_items = 1; break
                }
                if (has_items) {
                    print tt "<" sec ">"
                    for (i = 0; i < n; i++) {
                        if (cat(keys[i]) != sec) continue
                        if (side(keys[i]) != sl) continue
                        print ttt "<picsItem>"
                        print tttt "<itemNumber>" keys[i] "</itemNumber>"
                        print tttt "<feature/>"
                        print tttt "<reference/>"
                        print tttt "<status>O</status>"
                        print tttt "<support>" sups[i] "</support>"
                        print ttt "</picsItem>"
                    }
                    print tt "</" sec ">"
                } else {
                    print tt "<" sec "/>"
                }
            }
            print t "</clusterSide>"
        }

        # --- miscellaneous: items that have no S/C side at all ---
        has_misc = 0
        for (i = 0; i < n; i++) {
            if (cat(keys[i]) == "manually" && side(keys[i]) == "") { has_misc = 1; break }
        }
        if (has_misc) {
            print t "<miscellaneous>"
            for (i = 0; i < n; i++) {
                if (cat(keys[i]) != "manually") continue
                if (side(keys[i]) != "") continue
                print tt "<picsItem>"
                print ttt "<itemNumber>" keys[i] "</itemNumber>"
                print ttt "<feature/>"
                print ttt "<support>" sups[i] "</support>"
                print tt "</picsItem>"
            }
            print t "</miscellaneous>"
        }

        print "</clusterPICS>"
    }
    ' "$TMPFILE" > "$OUTFILE"

    echo "  Written: $OUTFILE"
    WRITTEN=$((WRITTEN + 1))
done

echo "Done — $WRITTEN file(s) written to $OUTPUT_DIR"
