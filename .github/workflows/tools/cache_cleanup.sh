#!/bin/bash

# Fetch the list of caches, sort them by size, and extract the keys and sizes
echo "Fetching and sorting caches by size..."
cache_list=$(gh api -H "Accept: application/vnd.github+json" \
  /repos/Elektrobit/ebcl_template/actions/caches \
  --jq '.actions_caches | sort_by(.size_in_bytes) | reverse | map({key: .key, size: .size_in_bytes})')

# Extract the largest cache key
largest_cache_key=$(echo "$cache_list" | jq -r '.[0].key')
largest_cache_size=$(echo "$cache_list" | jq -r '.[0].size')

echo "Largest cache: $largest_cache_key (${largest_cache_size} bytes)"

# Extract all other cache keys
other_cache_keys=$(echo "$cache_list" | jq -r '.[1:] | .[].key')

if [ -z "$other_cache_keys" ]; then
  echo "No other caches to delete."
  exit 0
fi

# Delete all caches except the largest
for key in $other_cache_keys; do
  echo "Deleting cache: $key"
  gh api -X DELETE -H "Accept: application/vnd.github+json" \
    /repos/Elektrobit/ebcl_template/actions/caches?key=$key
done

echo "All smaller caches deleted successfully."
