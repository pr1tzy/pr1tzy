#!/usr/bin/env bash
# GitHub profile revamp. Review each block before running it.
# Nothing here is destructive except the ARCHIVE block, which is reversible,
# and it never deletes a repository.
#
# Run top to bottom, or copy the blocks you want.
set -euo pipefail

USER=pr1tzy

# ---------------------------------------------------------------------------
# 0. URGENT: take the employer/partner hackathon repo out of public view.
#    It contains AceLink and Supervity agent prompts, integration notes and
#    webhook docs. No credentials are committed, but the content is not yours
#    to publish. Private is the safe default; delete it if you prefer.
# ---------------------------------------------------------------------------
gh repo edit "$USER/final_supervityr2" --visibility private --accept-visibility-change-consequences

# ---------------------------------------------------------------------------
# 1. Profile fields
# ---------------------------------------------------------------------------
gh api -X PATCH /user \
  -f name='Prithvi Singh' \
  -f bio='ML infrastructure and backend. Distributed training, retrieval, and the systems around them.' \
  -f location='Mumbai, India' \
  -f blog='https://ghostline.prithvisingh.fyi'

# ---------------------------------------------------------------------------
# 2. Descriptions and topics on the repos worth keeping visible
# ---------------------------------------------------------------------------
gh repo edit "$USER/ghostline" \
  --description 'Telemetry analysis for Assetto Corsa: 60 Hz lap recording, ghost comparison, and corner-by-corner time loss.' \
  --homepage 'https://ghostline.prithvisingh.fyi' \
  --add-topic telemetry --add-topic racing --add-topic python \
  --add-topic data-analysis --add-topic assetto-corsa --add-topic time-series

gh repo edit "$USER/mlopsproject" \
  --description 'Self-healing LLM QA service: continuous evaluation against a benchmark and live traffic, with automatic rollback on regression.' \
  --add-topic mlops --add-topic mlflow --add-topic dvc --add-topic jenkins \
  --add-topic llm --add-topic model-monitoring

gh repo edit "$USER/ParkiSense" \
  --description "Early Parkinson's screening from keystroke dynamics and drawing tremor, using wavelet and time-frequency features." \
  --add-topic machine-learning --add-topic signal-processing --add-topic healthcare

# Rename the mlops repo to something a recruiter can parse.
# GitHub keeps a redirect from the old name, so existing links still work.
gh repo rename self-healing-llm-qa --repo "$USER/mlopsproject" --yes

# ---------------------------------------------------------------------------
# 3. Archive the coursework. Archiving keeps them (and your contribution
#    graph) intact but marks them read-only and sinks them down the profile.
#    DAT8 is a copy of someone else's 2015 General Assembly course - that one
#    is worth deleting outright rather than archiving.
# ---------------------------------------------------------------------------
for r in SNLP_Assignments RL_Assignments aoml-assignments \
         Kapde-Ecommerce-Shopping streamlitaai MobileAppDev-BookLibrary; do
  gh repo archive "$USER/$r" --yes
done

# DAT8 is not your work and carries no credit. Delete it:
#   gh repo delete "$USER/DAT8" --yes
# (needs the delete_repo scope: gh auth refresh -h github.com -s delete_repo)

# ---------------------------------------------------------------------------
# 4. Pin the three that should lead. Replaces whatever is pinned now.
# ---------------------------------------------------------------------------
pin() {
  gh api graphql -f query='
    query($owner:String!, $name:String!){
      repository(owner:$owner, name:$name){ id }
    }' -f owner="$USER" -f name="$1" --jq '.data.repository.id'
}

IDS=$(printf '"%s",' "$(pin ghostline)" "$(pin self-healing-llm-qa)" "$(pin ParkiSense)" | sed 's/,$//')

gh api graphql -f query="
  mutation {
    replacePinnedItems(input:{pinnedItems:[$IDS]}) { clientMutationId }
  }"

echo
echo "Done. Check https://github.com/$USER"
