from utils import read_from_yaml, write_to_yaml
from processors import *
import shutil
import zipfile
import os
configfile: 'configurations.yaml'

DATA_RELEASE_STRUCT = ['L1A_L1B','L2OP-FB','L2OP-FT','L2OP-SI','L2OP-SM','L1A-SW-RX','L2-FDI']

rule CLEANUP:
    output: 'context/cleanup.yaml'
    run:
        if not config['dryMode']:
            dataFolder =  os.path.join(config['dataRoot'], 'DataRelease')
            shutil.rmtree(dataFolder)
            os.makedirs(dataFolder)
            for directory in DATA_RELEASE_STRUCT:
                os.makedirs(os.path.join(dataFolder, directory), exist_ok=True)
        write_to_yaml('context/cleanup.yaml', config)

rule LOAD:
    input:  rules.CLEANUP.output
    output: 'context/load.yaml'
    run:
        ctx = read_from_yaml(input[0])
        # unpack backup file into data root
        if (ctx['backupRoot'] and ctx['backupFile'] and not ctx['dryMode']):
            backup_zip = os.path.join(ctx['backupRoot'], f'{ctx["backupFile"]}.zip')
            with zipfile.ZipFile(backup_zip, 'r') as zip_ref:
                zip_ref.extractall(os.path.join(ctx['dataRoot'], 'DataRelease'))
        write_to_yaml('context/load.yaml', ctx)

rule L1_A:
    input: rules.CLEANUP.output
    output: 'context/L1_A.yaml'
    run:
        ctx = config
        p = L1_A(ctx, output[0])
        p.start()

rule L1_B:
    input:  rules.LOAD.output if config['start'] == 'L1_B' else rules.L1_A.output
    output: 'context/L1_B.yaml'
    run:
        ctx = read_from_yaml(input[0])
        p = L1_B(ctx, output[0])
        p.start()

rule L2_FT:
    input: rules.LOAD.output if config['start'] == 'L2_FT' else rules.L1_B.output
    output: 'context/L2_FT.yaml'
    run:
        ctx = read_from_yaml(input[0])
        p = L2_FT(ctx, output[0])
        p.start()

rule L2_FB:
    input: rules.LOAD.output if config['start'] == 'L2_FB' else rules.L1_B.output
    output: 'context/L2_FB.yaml'
    run:
        ctx = read_from_yaml(input[0])
        p = L2_FB(ctx, output[0])
        p.start()

rule L2_SM:
    input: rules.LOAD.output if config['start'] == 'L2_SM' else rules.L1_B.output
    output: f'context/L2_SM.yaml'
    run:
        ctx = read_from_yaml(input[0])
        p = L2_SM(ctx, output[0])
        p.start()

rule L2_SI:
    input: rules.LOAD.output if config['start'] == 'L2_SI' else rules.L1_B.output
    output: 'context/L2_SI.yaml'
    run:
        ctx = read_from_yaml(input[0])
        p = L2_SI(ctx, output[0])
        p.start()

rule TARGET:
    input: getattr(rules, config['end']).output
    run:
        ctx = read_from_yaml(input[0])
        if not config['dryMode']:
            if ctx['start'] != 'L1_A'
                backupFile_no_timestamp = ctx['backupFile'].split('_')
                del backupFile_no_timestamp[-1]
                ctx['backupFile'] = "_".join(backupFile_no_timestamp)
            archive_name = os.path.join(ctx['backupRoot'], f'{ctx["backupFile"]}_{ctx["timestamp"]}')
            folder_to_backup =  os.path.join(ctx['dataRoot'], 'DataRelease')
            shutil.make_archive(archive_name, 'zip', folder_to_backup)
            shutil.rmtree('context')

