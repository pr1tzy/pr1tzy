#!/usr/bin/env bash
# GitHub profile revamp. Safe to re-run: every step is idempotent.
#
# Git Bash on Windows (MSYS2) rewrites arguments that look like absolute unix
# paths, so `gh api /user` becomes `gh api C:/Program Files/Git/user`.
# MSYS_NO_PATHCONV=1 turns that off, and endpoints are written without a
# leading slash as a second line of defence.

export MSYS_NO_PATHCONV=1
USER=pr1tzy
fails=0

# Failures print the real error. An earlier version sent stderr to /dev/null,
# which turned "token is missing a scope" into a silent FAIL.
step() {
  local label="$1"; shift
  local out
  if out=$("$@" 2>&1); then
    printf '  ok    %s\n' "$label"
  else
    printf '  FAIL  %s\n' "$label"
    printf '        %s\n' "$(echo "$out" | tail -2 | tr '\n' ' ')"
    fails=$((fails + 1))
  fi
}

command -v gh >/dev/null 2>&1 || {
  echo "gh is not on PATH in this shell. Open a terminal where 'gh --version'"
  echo "works and run this again."
  exit 1
}

echo "0. Preflight"
if gh auth status 2>&1 | grep -q "'user'"; then
  printf '  ok    token has the user scope\n'
  HAVE_USER_SCOPE=1
else
  printf '  --    token is missing the "user" scope, so step 1 will be skipped.\n'
  printf '        Grant it (opens a browser), then re-run this script:\n'
  printf '          gh auth refresh -h github.com -s user\n'
  HAVE_USER_SCOPE=0
fi

echo
echo "1. Profile fields"
if [ "$HAVE_USER_SCOPE" = "1" ]; then
  step "bio, name, location, blog" \
    gh api -X PATCH user \
      -f name='Prithvi Singh' \
      -f bio='ML infrastructure and backend. Distributed training, retrieval, and the systems around them.' \
      -f location='Mumbai, India' \
      -f blog='https://ghostline.prithvisingh.fyi'
else
  printf '  skip  needs the user scope (see above)\n'
fi

echo
echo "2. Keep the hackathon repo private"
if [ "$(gh repo view "$USER/final_supervityr2" --json isPrivate --jq .isPrivate 2>/dev/null)" = "true" ]; then
  printf '  ok    already private\n'
else
  step "final_supervityr2 -> private" \
    gh repo edit "$USER/final_supervityr2" --visibility private --accept-visibility-change-consequences
fi

echo
echo "3. Descriptions and topics"
step "ghostline" \
  gh repo edit "$USER/ghostline" \
    --description 'Telemetry analysis for Assetto Corsa: 60 Hz lap recording, ghost comparison, and corner-by-corner time loss.' \
    --homepage 'https://ghostline.prithvisingh.fyi' \
    --add-topic telemetry --add-topic racing --add-topic python \
    --add-topic data-analysis --add-topic assetto-corsa --add-topic time-series

if gh repo view "$USER/mlopsproject" --json name >/dev/null 2>&1; then
  step "rename mlopsproject -> self-healing-llm-qa" \
    gh repo rename self-healing-llm-qa --repo "$USER/mlopsproject" --yes
else
  printf '  ok    already renamed to self-healing-llm-qa\n'
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
echo "4. Archive coursework (reversible)"
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
echo "5. Pins"
echo "  --    GitHub has no public API for pinning. Do this once by hand:"
echo "        https://github.com/$USER  ->  Customize your pins"
echo "        Tick: ghostline, self-healing-llm-qa, ParkiSense"

echo
if [ "$fails" -eq 0 ]; then
  echo "No failures. https://github.com/$USER"
else
  echo "$fails step(s) failed - see the messages above. Re-running is safe."
  exit 1
fi
