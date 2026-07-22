#!/usr/bin/env ruby
# frozen_string_literal: true

require "digest"
require "open3"
require "pathname"
require "set"
require "yaml"

ROOT = Pathname.new(__dir__).parent.expand_path
MANIFEST = ROOT / "manifest.yml"
INFRASTRUCTURE = Set.new([".gitattributes", ".gitignore", "README.md", "manifest.yml"])
REQUIRED = Set.new(%w[title date category source destination description status sha256])
LFS_SUFFIXES = Set.new(%w[.pdf .ppt .pptx .doc .docx .xls .xlsx .zip .7z .gz .tgz .xz .nar .opal .mp4 .mov])

def catalog_files
  ROOT.glob("**/*", File::FNM_DOTMATCH).select(&:file?).map do |path|
    relative = path.relative_path_from(ROOT).to_s
    next if path.each_filename.include?(".git")
    next if path.each_filename.include?(".github")
    next if path.each_filename.include?("scripts")
    next if INFRASTRUCTURE.include?(relative)

    relative
  end.compact.to_set
end

def lfs_filter(path)
  output, status = Open3.capture2e("git", "check-attr", "filter", "--", path, chdir: ROOT.to_s)
  raise "git check-attr failed for #{path}: #{output}" unless status.success?

  output.rpartition(":").last.strip
end

def error(message)
  warn "error: #{message}"
  1
end

data = YAML.safe_load(File.read(MANIFEST), permitted_classes: [], aliases: false)
unless data["schema-version"] == 1 && data["assets"].is_a?(Array)
  abort "error: manifest.yml must contain schema-version: 1 and an assets list"
end

errors = 0
destinations = Set.new

data["assets"].each_with_index do |asset, index|
  missing = REQUIRED - asset.keys.to_set
  unless missing.empty?
    errors += error("asset #{index + 1} is missing #{missing.to_a.sort.join(', ')}")
    next
  end

  destination = asset["destination"]
  path = ROOT / destination
  parts = Pathname(destination).each_filename.to_a
  destinations << destination

  errors += error("destination must be lowercase without spaces: #{destination}") if destination != destination.downcase || destination.include?(" ")
  valid_category = %w[presentations reports meetings tutorials examples datasets].include?(parts[0])
  valid_year = parts.length >= 3 && (parts[1] == "undated" || parts[1].match?(/^\d{4}$/))
  errors += error("destination must use <category>/<year>/...: #{destination}") unless valid_category && valid_year
  category_parts = asset["category"].split("/")
  errors += error("manifest category does not match destination: #{destination}") unless parts[0] == category_parts[0] && (category_parts.length == 1 || parts[2] == category_parts[1])

  unless path.file?
    errors += error("missing cataloged file: #{destination}")
    next
  end

  errors += error("SHA-256 mismatch: #{destination}") unless Digest::SHA256.file(path).hexdigest == asset["sha256"]
  errors += error("file is not covered by Git LFS attributes: #{destination}") if LFS_SUFFIXES.include?(path.extname.downcase) && lfs_filter(destination) != "lfs"

  date = asset["date"]
  if date.is_a?(String) && date.match?(/^\d{4}(-\d{2}){0,2}$/)
    errors += error("filename does not start with its known date: #{destination}") unless path.basename.to_s.start_with?(date)
    errors += error("year directory does not match the asset date: #{destination}") unless parts[1] == date[0, 4]
  end
end

actual = catalog_files
(actual - destinations).sort.each { |path| errors += error("uncataloged file: #{path}") }
(destinations - actual).sort.each { |path| errors += error("manifest destination is not an asset file: #{path}") }

abort "validation failed with #{errors} error(s)" unless errors.zero?

puts "validated #{destinations.length} cataloged document(s)"
