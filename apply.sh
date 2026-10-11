#!/usr/bin/env bash
# GitHub profile revamp. Safe to re-run: every step is idempotent.
#
# Git Bash on Windows (MSYS2) rewrites arguments that look like absolute unix
# paths, so `gh api /user` becomes `gh api C:/Program Files/Git/user`.
# MSYS_NO_PATHCONV=1 turns that off, and endpoints are written without a
# leading slash as a second line of defence.
#
# Steps report pass/fail individually instead of aborting the whole run.

export MSYS_NO_PATHCONV=1
USER=pr1tzy
fails=0

step() {
  local label="$1"; shift
  if "$@" >/dev/null 2>&1; then
    printf '  ok    %s\n' "$label"
  else
    printf '  FAIL  %s\n' "$label"
    fails=$((fails + 1))
  fi
}

echo "1. Profile fields"
step "bio, name, location, blog" \
  gh api -X PATCH user \
    -f name='Prithvi Singh' \
    -f bio='ML infrastructure and backend. Distributed training, retrieval, and the systems around them.' \
    -f location='Mumbai, India' \
    -f blog='https://ghostline.prithvisingh.fyi'

echo
echo "2. Keep the hackathon repo private (no-op if already private)"
step "final_supervityr2 -> private" \
  gh repo edit "$USER/final_supervityr2" --visibility private --accept-visibility-change-consequences

echo
echo "3. Descriptions and topics"
step "ghostline" \
  gh repo edit "$USER/ghostline" \
    --description 'Telemetry analysis for Assetto Corsa: 60 Hz lap recording, ghost comparison, and corner-by-corner time loss.' \
    --homepage 'https://ghostline.prithvisingh.fyi' \
    --add-topic telemetry --add-topic racing --add-topic python \
    --add-topic data-analysis --add-topic assetto-corsa --add-topic time-series

# Rename before editing, so the later steps address the new name.
if gh repo view "$USER/mlopsproject" >/dev/null 2>&1; then
  step "rename mlopsproject -> self-healing-llm-qa" \
    gh repo rename self-healing-llm-qa --repo "$USER/mlopsproject" --yes
fi

step "self-healing-llm-qa" \
  gh repo edit "$USER/self-healing-llm-qa" \
    --description 'Self-healing LLM QA service: continuous evaluation against a benchmark and live traffic, with automatic rollback on regression.' \
    --add-topic mlops --add-topic mlflow --add-topic dvc --add-topic jenkins \
    --add-topic llm --add-topic model-monitoring

step "ParkiSense" \
  gh repo edit "$USER/ParkiSense" \
    --description "Early Parkinson's screening from keystroke dynamics and drawing tremor, using wavelet and time-frequency features." \
    --add-topic machine-learning --add-topic signal-processing --add-topic healthcare

echo
echo "4. Archive coursework (reversible; keeps your contribution graph intact)"
for r in SNLP_Assignments RL_Assignments aoml-assignments \
         Kapde-Ecommerce-Shopping streamlitaai MobileAppDev-BookLibrary; do
  if [ "$(gh repo view "$USER/$r" --json isArchived --jq .isArchived 2>/dev/null)" = "true" ]; then
    printf '  ok    %s (already archived)\n' "$r"
  else
    step "$r" gh repo archive "$USER/$r" --yes
  fi
done

# DAT8 is a copy of someone else's 2015 General Assembly course. To remove it:
#   gh auth refresh -h github.com -s delete_repo
#   gh repo delete "$USER/DAT8" --yes

echo
echo "5. Pin the three that should lead"
pin_id() {
  gh api graphql -f query='query($owner:String!,$name:String!){repository(owner:$owner,name:$name){id}}' \
    -f owner="$USER" -f name="$1" --jq '.data.repository.id' 2>/dev/null
}
A=$(pin_id ghostline); B=$(pin_id self-healing-llm-qa); C=$(pin_id ParkiSense)
if [ -n "$A" ] && [ -n "$B" ] && [ -n "$C" ]; then
  step "ghostline, self-healing-llm-qa, ParkiSense" \
    gh api graphql -f query="mutation{replacePinnedItems(input:{pinnedItems:[\"$A\",\"$B\",\"$C\"]}){clientMutationId}}"
else
  printf '  FAIL  could not resolve all three repo ids\n'
  fails=$((fails + 1))
fi

echo
if [ "$fails" -eq 0 ]; then
  echo "All steps succeeded. https://github.com/$USER"
else
  echo "$fails step(s) failed. Re-run is safe; see messages above."
  exit 1
fi
