from utils import read_from_yaml, get_timestamp, write_to_yaml
from processors import *
import shutil
import os
configfile: 'configurations.yaml'

DATA_RELEASE_STRUCT = ['L1A_L1B','L2OP-FB','L2OP-FT','L2OP-SI','L2OP-SM','L1A-SW-RX','L2-FDI']

rule CLEANUP:
    output: 'context/cleanup.yaml'
    run:
        dataFolder =  os.path.join(config['dataRoot'], 'DataRelease')
        shutil.rmtree(dataFolder)
        os.makedirs(dataFolder)
        for directory in DATA_RELEASE_STRUCT:
            os.makedirs(os.path.join(dataFolder, directory), exist_ok=True)

rule L1_A:
    input: rules.CLEANUP.output
    output: 'context/L1_A.yaml'
    run:
        ctx = config
        p = L1_A(ctx, output[0])
        p.start(dry=config['dryMode'])

rule LOAD:
    output: 'context/load.yaml'
    input: os.path.join(config['backupRoot'], config['backupFile'])
    run:
        # unpack input file into data root
        write_to_yaml('context/load.yaml', config)

rule L1_B:
    input:  rules.LOAD.output if config['start'] == 'L1_B' else rules.L1_A.output
    output: 'context/L1_B.yaml'
    run:
        if config['start'] == 'L1_B':
            ctx = config
        else:
            ctx = read_from_yaml(input[0])
        p = L1_B(ctx, output[0])
        p.start(dry=config['dryMode'])

rule L2_FT:
    input: rules.LOAD.output if config['start'] == 'L2_FT' else rules.L1_B.output
    output: 'context/L2_FT.yaml'
    run:
        if config['start'] == 'L2_FT':
            ctx = config
        else:
            ctx = read_from_yaml(input[0])
        p = L2_FT(ctx, output[0])
        p.start(dry=config['dryMode'])

rule L2_FB:
    input: rules.LOAD.output if config['start'] == 'L2_FB' else rules.L1_B.output
    output: 'context/L2_FB.yaml'
    run:
        if config['start'] == 'L2_FB':
            ctx = config
        else:
            ctx = read_from_yaml(input[0])
        p = L2_FB(ctx, output[0])
        p.start(dry=config['dryMode'])

rule L2_SM:
    input: rules.LOAD.output if config['start'] == 'L2_SM' else rules.L1_B.output
    output: f'context/L2_SM.yaml'
    run:
        if config['start'] == 'L2_SM':
            ctx = config
        else:
            ctx = read_from_yaml(input[0])
        p = L2_SM(ctx, output[0])
        p.start(dry=config['dryMode'])

rule L2_SI:
    input: rules.LOAD.output if config['start'] == 'L2_SI' else rules.L1_B.output
    output: 'context/L2_SI.yaml'
    run:
        if config['start'] == 'L2_SI':
            ctx = config
        else:
            ctx = read_from_yaml(input[0])
        p = L2_SI(ctx, output[0])
        p.start(dry=config['dryMode'])

rule TARGET:
    input: getattr(rules, config['end']).output
    run:
        shutil.rmtree('context')
        archive_name = os.path.join(config['backupRoot'], f'{run-get_timestamp()}')
        folder_to_backup =  os.path.join(config['dataRoot'], 'DataRelease')
        shutil.make_archive(archive_name, 'zip', folder_to_backup)
