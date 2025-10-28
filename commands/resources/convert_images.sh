#!/bin/bash

# Convert SVG icons to PNG sizes.
# For each input SVG and each target size this script produces:
#   - <size>x<size>.png            : normal PNG export
#   - <size>x<size>-disabled.png   : grayscale / faded version (reduced alpha)
#   - <size>x<size>-dark.png       : darker variant (brightness reduced with ImageMagick)

for tool in magick; do # check required tool(s) — ImageMagick's 'magick' command
  if command -v $tool &> /dev/null; then
    echo "Found: $tool"
  else
    echo "Missing: $tool. Please install it via Homebrew"
    exit 1
  fi
done

# List of sizes to generate (width x height)
sizes=(16 32 64)

# Iterate over all SVG files in the current directory
for svg_file in *.svg; do
  # Extract filename without the .svg extension
  base_name=$(basename "$svg_file" .svg)

  # Create an output directory per icon (named after the base filename)
  output_dir="${base_name}"
  mkdir -p "$output_dir"

  echo "Converting: $svg_file -> $output_dir... "

  # Convert the SVG to each requested size
  for size in "${sizes[@]}"; do
    output_file="${output_dir}/${size}x${size}.png"
    output_file_disabled="${output_dir}/${size}x${size}-disabled.png"
  output_file_dark="${output_dir}/${size}x${size}-dark.png"
    
    magick "$svg_file" \
      -background none \
      -resize ${size}x${size} \
      "$output_file"

    magick "$svg_file" \
      -background none \
      -resize ${size}x${size} \
      -colorspace Gray \
      -alpha set -channel A -evaluate set 40% \
      "$output_file_disabled"

    # Create a darker variant (-dark) by lowering brightness.
    # -modulate takes Brightness,Saturation,Hue; 70 means 70% brightness (darker)
    magick "$svg_file" \
      -background none \
      -resize ${size}x${size} \
      -modulate 70,100,100 \
      "$output_file_dark"

    echo "Converted: ${size}px"
  done
done

echo "Done."