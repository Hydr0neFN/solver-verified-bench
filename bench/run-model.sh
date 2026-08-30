#!/usr/bin/env bash
# Sweep one model across all three tiers, matching each tier's trial count.
#   usage: bash run-model.sh <model-slug> [parallelism]
# Skips any cell that already has a non-empty output, so it is safe to re-run
# after a quota block.
set -u
cd "$(dirname "$0")" || exit 1

M="${1:?usage: run-model.sh <model-slug> [parallelism]}"
P="${2:-6}"
mkdir -p out out2 out3 log log2 log3

JOBS="joblist-${M}.txt"
: > "$JOBS"
for f in tasks/*.txt;  do t=$(basename "$f" .txt); for n in 1 2;       do echo "1|$t|$n" >> "$JOBS"; done; done
for f in tasks2/*.txt; do t=$(basename "$f" .txt); for n in 1 2 3;     do echo "2|$t|$n" >> "$JOBS"; done; done
for f in tasks3/*.txt; do t=$(basename "$f" .txt); for n in 1 2 3 4 5; do echo "3|$t|$n" >> "$JOBS"; done; done

run_one() {
  IFS='|' read -r tier t n <<< "$1"
  case "$tier" in
    1) td=tasks;  od=out;  ld=log;  tim=timings.csv;  pt=6m;  to=420 ;;
    2) td=tasks2; od=out2; ld=log2; tim=timings2.csv; pt=10m; to=700 ;;
    3) td=tasks3; od=out3; ld=log3; tim=timings3.csv; pt=10m; to=700 ;;
  esac
  outf="${od}/${t}__${M}__t${n}.txt"
  [ -s "$outf" ] && return 0
  start=$(date +%s%3N)
  timeout "$to" agy -p "$(cat "${td}/${t}.txt")" \
      --model "$M" --output-format text --print-timeout "$pt" \
      --dangerously-skip-permissions \
      > "$outf" 2> "${ld}/${t}__${M}__t${n}.err"
  rc=$?
  end=$(date +%s%3N)
  echo "${t}|${M}|${n}|${rc}|$((end-start))" >> "$tim"
}
export -f run_one
export M

cat "$JOBS" | xargs -P "$P" -I{} bash -c 'run_one "$@"' _ {}
echo "DONE ${M}: $(wc -l < "$JOBS") jobs"
