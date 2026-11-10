#!/usr/bin/env python3
"""Authorized ten-step R2 bend; discrete ZeroSC identity gates charged run."""
import run_tracking as driver

selected=[]
for zero in [True, False]:
    directory, manifest = driver.prepare('bend', zero)
    driver.run(directory, manifest)
    selected.append(str(directory/'manifest.json'))
    driver.dump(driver.ROOT/'selected-bend.json', selected)
