import argparse
import uproot
import h5py
import numpy as np
from rich.console import Console
from rich.progress import track
import json
from pathlib import Path

console = Console()

def get_grid_cell_phi(phi):
    #console.print(phi)
    the_bin = np.clip(
        np.digitize(phi, bins=np.linspace(-3.1415, 3.1415, num=17))-1,
        a_min=0,
        a_max=15
    )
    #console.print(the_bin)
    return the_bin

def get_grid_cell_eta(eta):
    the_bin = np.clip(
        np.digitize(eta, bins=np.linspace(-3.0, 3.0, num=17))-1,
        a_min=0,
        a_max=15,
    )
    return the_bin

def process_particles(
        event_image_data,
        batch,
        batch_index,
        nParticle,
        particle_pt,
        particle_eta,
        particle_phi,
        particle_m,
        particle_id):
    for particle_index in range(batch[nParticle][batch_index]):
        eta = batch[particle_eta][batch_index][particle_index]
        if eta > 3.0 or eta < -3.0:
            continue
        pt = batch[particle_pt][batch_index][particle_index]
        phi = batch[particle_phi][batch_index][particle_index]
        m = batch[particle_m][batch_index][particle_index]
        ID = particle_id
        grid_cell_phi_index = get_grid_cell_phi(phi)
        grid_cell_eta_index = get_grid_cell_eta(eta)

        if event_image_data[batch_index, grid_cell_phi_index, grid_cell_eta_index, 0] == 0.0 or pt > event_image_data[batch_index, grid_cell_phi_index, grid_cell_eta_index, 0]:
            event_image_data[batch_index, grid_cell_phi_index, grid_cell_eta_index, 0] = pt
            event_image_data[batch_index, grid_cell_phi_index, grid_cell_eta_index, 1] = eta
            event_image_data[batch_index, grid_cell_phi_index, grid_cell_eta_index, 2] = phi
            event_image_data[batch_index, grid_cell_phi_index, grid_cell_eta_index, 3] = m
            event_image_data[batch_index, grid_cell_phi_index, grid_cell_eta_index, 4] = ID
    return event_image_data

# This should make a 20 by 20 grid of reco particles
# in between eta -3 to eta 3
# and full phi
# It will have only a few features
# object pt
# object eta
# object phi
# object m
# object type encoded as (1 = jets, 2 = electrons, 3=photons, 4=muons, 5=taus)
#We'll take the highest pt object in a cell

def process_data(list_of_files, limit_events=None):
    files_plus_tree = [x+':Events' for x in list_of_files]
    nBatches = 0
    processed_events = 0
    event_data = None
    for batch in track(uproot.iterate(files_plus_tree), description="Processing files...", console = console):
        console.log(f'Processing batch: {nBatches}')

        event_image_data = np.zeros((len(batch), 16, 16, 5))

        for i in range(len(batch)):
            event_image_data = process_particles(
                event_image_data,
                batch,
                i,
                nParticle='nJet',
                particle_pt='Jet_pt',
                particle_eta='Jet_eta',
                particle_phi='Jet_phi',
                particle_m='Jet_mass',
                particle_id=1.0,
            )

            event_image_data = process_particles(
                event_image_data,
                batch,
                i,
                nParticle='nElectron',
                particle_pt='Electron_pt',
                particle_eta='Electron_eta',
                particle_phi='Electron_phi',
                particle_m='Electron_mass',
                particle_id=2.0,
            )

            event_image_data = process_particles(
                event_image_data,
                batch,
                i,
                nParticle='nPhoton',
                particle_pt='Photon_pt',
                particle_eta='Photon_eta',
                particle_phi='Photon_phi',
                particle_m='Photon_mass',
                particle_id=3.0,
            )

            event_image_data = process_particles(
                event_image_data,
                batch,
                i,
                nParticle='nMuon',
                particle_pt='Muon_pt',
                particle_eta='Muon_eta',
                particle_phi='Muon_phi',
                particle_m='Muon_mass',
                particle_id=1.0,
            )
            
            event_image_data = process_particles(
                event_image_data,
                batch,
                i,
                nParticle='nTau',
                particle_pt='Tau_pt',
                particle_eta='Tau_eta',
                particle_phi='Tau_phi',
                particle_m='Tau_mass',
                particle_id=1.0,
            )
        if event_data is None:
            event_data = event_image_data
        else:
            event_data = np.append(
                event_data,
                event_image_data,
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
        the_file.create_dataset('event_image_data', data=event_data)
        
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
        help='Stop processing after a certain number of handled events, due to the large amount of particle data present'
    )

    args = parser.parse_args()

    main(args)
