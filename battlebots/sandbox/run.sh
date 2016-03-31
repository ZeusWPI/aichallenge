#!/usr/bin/bash
#
# Run a jailed compile job in a specific directory
# Usage: run.sh <bot dir> <compile cmd>

set -euo pipefail

this_script_dir="$(dirname "$BASH_SOURCE")"
bot_dir="$1"
if [[ ! -d "${bot_dir}" ]]; then
    echo "Please supply a directory as the first argument" >&2
    exit 1
fi
shift

unsafe_bot_script=$(mktemp -p "${bot_dir}" bot_XXXXX.sh)
{
    echo "$@"
} >"${unsafe_bot_script}"
chmod +x "${unsafe_bot_script}"

# Set bot dir as user home dir and allow writes to it
/usr/bin/firejail \
    --profile="${this_script_dir}/bot.profile" \
    --private="${bot_dir}" \
    --whitelist="${bot_dir}" \
    -- \
    "$HOME/$(basename ${unsafe_bot_script})"

rm "${unsafe_bot_script}"
