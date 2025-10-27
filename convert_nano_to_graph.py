import argparse
import uproot
import h5py
import numpy as np
from rich.console import Console
from rich.progress import track
import json
from pathlib import Path
import awkward as ak

from sklearn.neighbors import NearestNeighbors
from torch_geometric.data import Data
import torch

console = Console()

def make_graph(particle_list, k=3):
    actual_neighbors=min(len(particle_list), k+1)
    nbrs = NearestNeighbors(n_neighbors=actual_neighbors).fit(particle_list[:, 1:3])
    _, indices = nbrs.kneighbors(particle_list[:, 1:3])

    src = []
    dst = []

    for i, neighbors in enumerate(indices):
        for j in neighbors[1:]:
            src.append(i)
            dst.append(j)
    edge_index = torch.tensor([src, dst])
    x=torch.tensor(particle_list)

    return Data(x=x, edge_index = edge_index)

def process_data(list_of_files, limit_events=None):
    files_plus_tree = [x+':Events' for x in list_of_files]
    nBatches = 0
    processed_events = 0
    event_data = []
    npfcands = 0
    for batch in track(uproot.iterate(files_plus_tree), description="Processing files...", console = console):
        console.log(f'Processing batch: {nBatches}')

        #console.print(type(batch))
        #console.print(batch)
        for event in range(len(batch)):
            features = ak.to_numpy(ak.zip({
                'particle_pt': batch['PFCands_pt'][event],
                'particle_eta': batch['PFCands_eta'][event],
                'particle_phi': batch['PFCands_phi'][event],
                'particle_mass': batch['PFCands_mass'][event],
                #'particle_charge': batch['PFCands_charge'][event],
                'particle_PDG_ID': batch['PFCands_pdgId'][event],
                #'particle_d0': batch['PFCands_d0'][event],
                #'particle_dz': batch['PFCands_dz'][event],
            }))
            features = list(features)
            features = [list(x) for x in features]
            features = np.array(features)
            # Take the 75 highest pt pf cands
            features_sort = np.argsort(features[:, 0])
            features = features[features_sort]
            #Select 75 random pf cands
            #np.random.shuffle(features)
            features = features[:40] #save space and consider only 100 pf Cands
            npfcands += len(features)
            # console.print(features)
            # console.print(len(features))
            # console.print(features.shape)
            graph = make_graph(features, k=3)
            #console.print(graph)
            event_data.append(graph)
            processed_events += 1
            #console.log(processed_events)
            if limit_events is not None and processed_events >= limit_events:
                break
        nBatches += 1
        if limit_events is not None and processed_events >= limit_events:
            break
    console.log(f'Average PFCands per event: {npfcands/processed_events:.4g}')
    return event_data

def main(args):
    console.log('\[Start]')

    output_path = Path(args.output_path)
    output_path.mkdir(parents=True, exist_ok=True)
    output_file = f'{output_path}/{args.output_file}.pt'

    console.log(f'Output file: {output_file}')
    
    files_to_process = args.files

    event_data = process_data(files_to_process, limit_events=args.limit_events)
    #event_data = process_data(files_to_process, limit_events=100)

    total_events = len(event_data)
    console.log(f'Total number of events processed: {total_events}')
    
    torch.save(event_data, f'{output_file}')

    console.log('\[Done]')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Basic conversion script for CMS open data nano AOD pytorch graph datasets')

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
        help='Stop processing after a certain number of handled events, due to the large amount of particle data present'
    )

    args = parser.parse_args()

    main(args)
