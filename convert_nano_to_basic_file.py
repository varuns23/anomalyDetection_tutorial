#!/usr/bin/env python3
# Basic script for converting cms open data nano AOD zero bias
# into a basic file .h5 file for doing AD with basic techniques

import argparse
import uproot
import h5py
import numpy as np
from rich.console import Console
from rich.progress import track
import json
from pathlib import Path

console = Console()

# Use uproot to quickly get a bunch of particle multiplicity and MET data from
# nano AOD
def process_data(list_of_files):
    files_plus_tree = [x+':Events' for x in list_of_files]
    nBatches = 0
    event_data = None
    for batch in track(uproot.iterate(files_plus_tree), description='Processing files...', console = console):
        console.log(f'Processing batch: {nBatches}')

        event_multiplicities = np.stack(
            [
                np.array(batch.nJet),
                np.array(batch.nMuon),
                np.array(batch.nElectron),
                np.array(batch.nPhoton),
                np.array(batch.nTau),
                np.array(batch.nFatJet),
                np.array(batch.nboostedTau),
                np.array(batch.PuppiMET_pt)
            ],
            axis=1
        )
        if event_data is None:
            event_data = event_multiplicities
        else:
            event_data = np.append(event_data, event_multiplicities, axis=0)
        nBatches += 1
    event_data = np.array(event_data)
    return event_data

def main(args):
    console.log('\[Start]')

    output_path = Path(args.output_path)
    output_path.mkdir(parents=True, exist_ok=True)
    output_file = f'{output_path}/{args.output_file}'

    console.log(f'Output file: {output_file}')
    
    files_to_process = args.files

    event_data = process_data(files_to_process)

    total_events = len(event_data)
    console.log(f'Total number of events processed: {total_events}')

    with h5py.File(output_file,'w') as the_file:
        the_file.create_dataset('basic_event_data', data=event_data)
        
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

    args = parser.parse_args()

    main(args)
