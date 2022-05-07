rule test:
    output: 'output.txt'
    shell:
        '''
        'Hello, World!' | Out-File -FilePath {output}
        '''