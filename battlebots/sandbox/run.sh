#!/usr/bin/bash
#
# Run a jailed compile job in a specific directory
# Usage: run.sh <bot dir> <compile cmd>

set -euo pipefail

this_script_dir="$(dirname "$BASH_SOURCE")"
bot_dir="$1"
shift

# Set bot dir as user home dir and allow writes to it
/usr/bin/firejail \
    --profile="${this_script_dir}/bot.profile" \
    --private="${bot_dir}" \
    --whitelist="${bot_dir}" \
    -- \
    "$@"
