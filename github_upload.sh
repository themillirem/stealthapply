#!/usr/bin/env bash
# StealthApply — GitHub upload script
# TOKEN is passed via environment variable, never stored in this file.
#
# Usage:
#   cd /Users/vaprz/.openclaw/workspace/stealthapply
#   GH_TOKEN=<your_token> bash github_upload.sh

set -e

REPO_NAME="stealthapply"

if [ -z "$GH_TOKEN" ]; then
  echo "❌  GH_TOKEN environment variable is required."
  echo "    Usage: GH_TOKEN=<token> bash github_upload.sh"
  exit 1
fi

echo "🎯  StealthApply — GitHub Upload"
echo "================================"

echo "→ Getting GitHub username..."
GH_USER=$(curl -s -H "Authorization: token $GH_TOKEN" https://api.github.com/user \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['login'])")
echo "  Logged in as: $GH_USER"

echo "→ Creating GitHub repo '$REPO_NAME'..."
RESPONSE=$(curl -s -X POST \
  -H "Authorization: token $GH_TOKEN" \
  -H "Content-Type: application/json" \
  https://api.github.com/user/repos \
  -d "{
    \"name\": \"$REPO_NAME\",
    \"description\": \"Privacy-first stealth resume submission tool for SolidWorks engineers\",
    \"private\": false,
    \"auto_init\": false
  }")

echo "$RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if 'html_url' in data:
    print('  ✅ Repo created:', data['html_url'])
elif data.get('errors', [{}])[0].get('message', '') == 'name already exists on this account':
    print('  ℹ️  Repo already exists, continuing...')
else:
    print('  Response:', json.dumps(data, indent=2))
" 2>/dev/null || true

echo "→ Setting up git..."
git init -b main 2>/dev/null || git checkout -b main 2>/dev/null || true
git add .
git diff --cached --quiet && echo "  ℹ️  Nothing new to commit." || \
  git commit -m "feat: initial StealthApply release

- tkinter dark-themed GUI (Catppuccin-inspired)
- PDF and DOCX resume upload and parsing
- Ollama local LLM integration for tailored cover notes
- In-memory transaction receipts (saveable on demand)
- 17 pre-loaded SolidWorks engineering companies in Minneapolis-St. Paul
- Privacy-first: no data written to disk without user consent
- Configurable LLM model and Ollama URL via settings dialog
- Clean separation: config, parser, scraper, LLM client, submitter, GUI"

git remote remove origin 2>/dev/null || true
git remote add origin "https://${GH_USER}:${GH_TOKEN}@github.com/${GH_USER}/${REPO_NAME}.git"
git push -u origin main

echo ""
echo "✅  Done!"
echo "   https://github.com/${GH_USER}/${REPO_NAME}"
