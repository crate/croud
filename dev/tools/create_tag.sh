#!/bin/bash
# Version: 0.1

function print_error() {
  echo -e "\033[31mERROR:\033[0m $1"
}

function print_info() {
  echo -e "\033[32mINFO:\033[0m  $1"
}

# check if everything is committed
if ! [[ -z "$(git status -s)" ]]; then
  print_error "Working directory not clean."
  print_error "Please commit all changes before tagging."
  exit 1
fi

print_info "Fetching origin ..."
git fetch origin > /dev/null

# get current branch
BRANCH=`git branch | grep "^*" | cut -d " " -f 2`
print_info "Current branch is $BRANCH."

# check if local branch is origin branch
LOCAL_COMMIT=`git show --format="%H" $BRANCH`
ORIGIN_COMMIT=`git show --format="%H" origin/$BRANCH`

if [[ "$LOCAL_COMMIT" != "$ORIGIN_COMMIT" ]]; then
  print_error "Local $BRANCH is not up to date."
  exit 1
fi

# check if tag to create has already been created
if ! [[ -x $(command -v python3) ]]; then
  print_error "Python 3 could not be found."
  exit 1
fi
PKG_DIR="$(dirname $0)/../.."
VERSION=$(python3 $PKG_DIR/setup.py --version)
print_info "Package version is $VERSION"

if [[ "$VERSION" == "$(git tag | grep $VERSION)" ]]; then
  print_error "Version $VERSION already tagged."
  exit 1
fi

# check if VERSION is in head of CHANGES.rst
REV_NOTE=$(grep -E "$VERSION - [0-9/]{10}" CHANGES.rst)
if [[ -z "$REV_NOTE" ]]; then
  print_error "No notes for version $VERSION found in CHANGES.rst."
  exit 1
fi
print_info "Changelog section: $REV_NOTE"

print_info "Creating tag $VERSION ..."

git tag -a "$VERSION" -m "Tag for version $VERSION"
git push --tags

print_info "Done."
