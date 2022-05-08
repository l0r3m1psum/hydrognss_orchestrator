from utils import read_from_yaml
from processors import *
import shutil
configfile: 'configurations.yaml'


rule L1_A:
    output: 'context/L1_A.yaml'
    run:
        ctx = config
        p = L1_A(ctx, output[0])
        p.run()

rule L1_B:
    input:  [] if config['start'] == 'L1_B' else rules.L1_A.output
    output: 'context/L1_B.yaml'
    run:
        if config['start'] == 'L1_B':
            ctx = config
        else:
            ctx = read_from_yaml(input[0])
        p = L1_B(ctx, output[0])
        p.run()

rule L2_FT:
    input: [] if config['start'] == 'L2_FT' else rules.L1_B.output
    output: 'context/L2_FT.yaml'
    run:
        if config['start'] == 'L2_FT':
            ctx = config
        else:
            ctx = read_from_yaml(input[0])
        p = L2_FT(ctx, output[0])
        p.run()

rule L2_FB:
    input: [] if config['start'] == 'L2_FB' else rules.L1_B.output
    output: 'context/L2_FB.yaml'
    run:
        if config['start'] == 'L2_FB':
            ctx = config
        else:
            ctx = read_from_yaml(input[0])
        p = L2_FB(ctx, output[0])
        p.run()

rule L2_SM:
    input: [] if config['start'] == 'L2_SM' else rules.L1_B.output
    output: f'context/L2_SM.yaml'
    run:
        if config['start'] == 'L2_SM':
            ctx = config
        else:
            ctx = read_from_yaml(input[0])
        p = L2_SM(ctx, output[0])
        p.run()

rule L2_SI:
    input: [] if config['start'] == 'L2_SI' else rules.L1_B.output
    output: 'context/L2_SI.yaml'
    run:
        if config['start'] == 'L2_SI':
            ctx = config
        else:
            ctx = read_from_yaml(input[0])
        p = L2_SI(ctx, output[0])
        p.run()

rule TARGET:
    input: getattr(rules, config['end']).output
    run:
        shutil.rmtree('context')
