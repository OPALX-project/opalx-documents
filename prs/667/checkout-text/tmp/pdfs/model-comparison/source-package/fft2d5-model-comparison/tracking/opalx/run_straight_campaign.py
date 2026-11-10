#!/usr/bin/env python3
"""Authorized ten-step straight ZeroSC then charged original 2D5 comparison."""
import run_tracking as driver

selected=[]
for zero in [True, False]:
    directory, manifest = driver.prepare('straight', zero)
    driver.run(directory, manifest)
    selected.append(str(directory/'manifest.json'))
    driver.dump(driver.ROOT/'selected-straight.json', selected)
