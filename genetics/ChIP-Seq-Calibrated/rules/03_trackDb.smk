rule trackDb:
    input:
        bam_coverage_bw_targets(),
    output:
        os.path.join(config["analysis_name"]+os.sep+config["track"], "trackDb.txt"),
    params:
        track_base_url=track_base_url,
        bigwigs=config["analysis_name"]+os.sep+config["bam_coverage"],
    log:
        os.path.join(config["analysis_name"], "logs/12_track/trackDb.txt"),
    run:
        with open(str(output), 'w') as nfile:
            for idx, bw in enumerate(sorted(map(str, input))):
                name = bw.split('.bw')[0].split('/')[-1]
                nfile.write('track %s\n'%name)
                nfile.write('bigDataUrl %s/%s.bw\n'%(params.track_base_url, name))
                nfile.write('shortLabel %s\n'%name)
                nfile.write('longLabel %s\n'%name)
                nfile.write('type bigWig\n')
                nfile.write('visibility full\n')
                nfile.write('autoScale on\n')
                nfile.write('priority 1\n\n')
