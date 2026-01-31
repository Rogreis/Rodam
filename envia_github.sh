#!/bin/bash

versao="1.0.1"

git tag -d v${versao}
git push --delete origin v${versao}
git tag v${versao}
git push origin --tags
git tag -n
