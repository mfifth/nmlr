# Release Checklist

## Pre-Release
- [ ] Bump version in CITATION.cff if needed
- [ ] Update CHANGELOG.md with release notes
- [ ] Run full test suite: `pytest`
- [ ] Ensure no secrets in repo
- [ ] Update README badges if needed

## Release
- [ ] Tag release: `git tag v0.1.1 && git push origin v0.1.1`
- [ ] Create GitHub release with summary of changes
- [ ] Attach `accuracy_by_method.png` to release assets

## DOI (Zenodo)
- [ ] Connect GitHub repo to Zenodo
- [ ] Mint DOI for the release
- [ ] Add DOI badge to README: `[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://zenodo.org/badge/latestdoi/XXXXXXX)`
- [ ] Update CITATION.cff with DOI
