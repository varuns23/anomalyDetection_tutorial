#!/usr/bin/env python3
# Basic script for converting cms open data nano AOD 
# into a basic file .h5 file for doing AD with intermediate techniques

import argparse
import uproot
import h5py
import numpy as np
from rich.console import Console
from rich.progress import track
import json
from pathlib import Path

console = Console()

#Variables to use in the jets:
# jet pt
# jet eta
# jet phi
# jet mass
# jet nconstituents
# jet nelectrons
# jet nmuons
# jet charged hadron fraction
# jet neutral hadron fraction
# Jet_btagDeepB
# Jet_btagDeepCvB
# Jet_btagDeepCvL
# jet area
# Jet_btagDeepFlavB
# Jet_btagDeepFlavCvB
# Jet_btagDeepFlavCvL
# Jet_btagDeepFlavQG
# 17 Variables

# Use uproot to quickly get a bunch of jet data from nano AOD
def process_data(list_of_files, limit_events=None):
    files_plus_tree = [x+':Events' for x in list_of_files]
    nBatches = 0
    processed_events = 0
    event_data = None
    for batch in track(uproot.iterate(files_plus_tree), description="Processing files...", console = console):
        console.log(f'Processing batch: {nBatches}')

        event_jet_data = np.zeros((len(batch), 8, 17))

        for i in range(len(batch)):
            for j in range(min(batch['nJet'][i], 8)):
                event_jet_data[i, j, 0] = batch['Jet_pt'][i][j]
                event_jet_data[i, j, 1] = batch['Jet_eta'][i][j]
                event_jet_data[i, j, 2] = batch['Jet_phi'][i][j]
                event_jet_data[i, j, 3] = batch['Jet_mass'][i][j]
                event_jet_data[i, j, 4] = batch['Jet_nConstituents'][i][j]
                event_jet_data[i, j, 5] = batch['Jet_nElectrons'][i][j]
                event_jet_data[i, j, 6] = batch['Jet_nMuons'][i][j]
                event_jet_data[i, j, 7] = batch['Jet_chHEF'][i][j]
                event_jet_data[i, j, 8] = batch['Jet_neHEF'][i][j]
                event_jet_data[i, j, 9] = batch['Jet_btagDeepB'][i][j]
                event_jet_data[i, j, 10] = batch['Jet_btagDeepCvB'][i][j]
                event_jet_data[i, j, 11] = batch['Jet_btagDeepCvL'][i][j]
                event_jet_data[i, j, 12] = batch['Jet_area'][i][j]
                event_jet_data[i, j, 13] = batch['Jet_btagDeepFlavB'][i][j]
                event_jet_data[i, j, 14] = batch['Jet_btagDeepFlavCvB'][i][j]
                event_jet_data[i, j, 15] = batch['Jet_btagDeepFlavCvL'][i][j]
                event_jet_data[i, j, 16] = batch['Jet_btagDeepFlavQG'][i][j]
        if event_data is None:
            event_data = event_jet_data
        else:
            event_data = np.append(
                event_data,
                event_jet_data,
                axis=0,
            )
        nBatches += 1
        processed_events += len(batch)
        if limit_events is not None and processed_events >= limit_events:
            break
    event_data = np.array(event_data)
    return event_data

def main(args):
    console.log('\[Start]')

    output_path = Path(args.output_path)
    output_path.mkdir(parents=True, exist_ok=True)
    output_file = f'{output_path}/{args.output_file}'

    console.log(f'Output file: {output_file}')
    
    files_to_process = args.files

    event_data = process_data(files_to_process, limit_events=args.limit_events)

    total_events = len(event_data)
    console.log(f'Total number of events processed: {total_events}')

    with h5py.File(output_file,'w') as the_file:
        the_file.create_dataset('jet_event_data', data=event_data)
        
    console.log('\[Done]')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Basic conversion script for CMS open data nano AOD to .h5s')

    parser.add_argument(
        'output_path',
        nargs='?',
        help='Final path to store the output .h5 file in',
    )

    parser.add_argument(
        'output_file',
        nargs='?',
        help='Final name for the output file'
    )
    
    parser.add_argument(
        'files',
        nargs='+',
        help='JSON config file to run the script'
    )

    parser.add_argument(
        '--limit_events',
        nargs='?',
        type=int,
        help='Stop processing after a certain number of handled events, due to the large amount of jet data present'
    )

    args = parser.parse_args()

    main(args)
