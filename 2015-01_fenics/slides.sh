#!/bin/bash

ipython nbconvert \
  "Resolviendo ecuaciones diferenciales con FEniCS.ipynb" \
  --to slides --post serve \
  --reveal-prefix='http://cdn.jsdelivr.net/reveal.js/2.5.0'
