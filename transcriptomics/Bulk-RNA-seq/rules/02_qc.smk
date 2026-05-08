genomeV = config['genome_built_version']

rule fastq_fastqc:
    input:
        os.path.join(config["analysis_name"]+os.sep+config["reads"], "{sample_or}.fastq.gz"),
    output:
        html=os.path.join(config["analysis_name"]+os.sep+config["reads_qc"], "{sample_or}.html"),
        zip=os.path.join(config["analysis_name"]+os.sep+config["reads_qc"], "{sample_or}_fastqc.zip"),
    params: "--quiet"
    log:
        os.path.join(config["analysis_name"], "logs/01_move_fastq/{sample_or}_fastqc.txt"),
    threads: 1
    shell:
        """
            mkdir -p $(dirname {output.html})
            fastqc {params} --threads {threads} --outdir $(dirname {output.html}) {input} > {log} 2>&1
            mv $(dirname {output.html})/{wildcards.sample_or}_fastqc.html {output.html}
        """

rule trimming_fastqc:
    input:
        os.path.join(config["analysis_name"]+os.sep+config["trimming"], "{sample_or}.fastq.gz"),
    output:
        os.path.join(config["analysis_name"]+os.sep+config["trimming_qc"], "{sample_or}_fastqc.txt"),
    params:
        input_fastq=os.path.join(config["analysis_name"]+os.sep+config["trimming"], "{sample_or}.fastq.gz"),
        input_fastq_orphan=os.path.join(config["analysis_name"]+os.sep+config["trimming"], "{sample_or}_orphan.fastq.gz"),
        thread="1",
        folder=os.path.join(config["analysis_name"]+os.sep+config["trimming_qc"]),
        end=config["single_paired_end"],
    log:
        os.path.join(config["analysis_name"], "logs/02_trimming/{sample_or}_fastqc.txt"),
    shell:
        """
            mkdir -p {params.folder}

            fastqc --quiet --noextract --threads {params.thread} --outdir {params.folder} {params.input_fastq}
            
            if [ {params.end} == "paired" ]
            then
                fastqc --quiet --noextract --threads {params.thread} --outdir {params.folder} {params.input_fastq_orphan}
            fi
            
            echo trimming_fastqc Done! >> {output}
        """
        
        
rule star_stats:
    input:
        bam=os.path.join(config["analysis_name"]+os.sep+config["star"], "{sample}Aligned.out.bam"),
    output:
        os.path.join(config["analysis_name"]+os.sep+config["star_qc"], "{sample}_%s_stats.txt"%genomeV),
    params:
        extra="",
    log:
        os.path.join(config["analysis_name"], "logs/03_star/{sample}_%s_stats.txt"%genomeV),
    shell:
        """
            mkdir -p $(dirname {output})
            samtools stats {params.extra} {input.bam} > {output} 2> {log}
        """

        
rule star_multiqc:
    input:
        os.path.join(config["analysis_name"]+os.sep+config["star_qc"], "{sample}_%s_stats.txt"%genomeV),
    output:
        os.path.join(config["analysis_name"]+os.sep+config["star_qc"], "{sample}_%s_multiqc.html"%genomeV),
    params:
        extra="",
    log:
        os.path.join(config["analysis_name"], "logs/03_star/{sample}_%s_multiqc.txt"%genomeV),
    shell:
        """
            mkdir -p $(dirname {output})
            multiqc --force {params.extra} -n $(basename {output}) -o $(dirname {output}) {input} > {log} 2>&1
        """
        
        
rule sorted_dedup_stats:
    input:
        bam=os.path.join(config["analysis_name"]+os.sep+config["duplicates"], "{sample_merged}_%s.bam"%genomeV),
    output:
        os.path.join(config["analysis_name"]+os.sep+config["duplicates_qc"], "{sample_merged}_%s_stats.txt"%genomeV),
    params:
        extra="",
    log:
        os.path.join(config["analysis_name"], "logs/06_mark_duplicates/{sample_merged}_%s_stats.txt"%genomeV),
    shell:
        """
            mkdir -p $(dirname {output})
            samtools stats {params.extra} {input.bam} > {output} 2> {log}
        """

        
rule sorted_dedup_multiqc:
    input:
        os.path.join(config["analysis_name"]+os.sep+config["duplicates_qc"], "{sample_merged}_%s_stats.txt"%genomeV),
    output:
        os.path.join(config["analysis_name"]+os.sep+config["duplicates_qc"], "{sample_merged}_%s_multiqc.html"%genomeV),
    params:
        extra="",
    log:
        os.path.join(config["analysis_name"], "logs/06_mark_duplicates/{sample_merged}_%s_multiqc.txt"%genomeV),
    shell:
        """
            mkdir -p $(dirname {output})
            multiqc --force {params.extra} -n $(basename {output}) -o $(dirname {output}) {input} > {log} 2>&1
        """


rule merge_stats:
    input:
        bam=os.path.join(config["analysis_name"]+os.sep+config["merge"], "{sample_merged}_%s.bam"%genomeV),
    output:
        os.path.join(config["analysis_name"]+os.sep+config["merge_qc"], "{sample_merged}_%s_stats.txt"%genomeV),
    params:
        extra="",
    log:
        os.path.join(config["analysis_name"], "logs/07_merge/{sample_merged}_%s_stats.txt"%genomeV),
    shell:
        """
            mkdir -p $(dirname {output})
            samtools stats {params.extra} {input.bam} > {output} 2> {log}
        """

        
rule merge_multiqc:
    input:
        os.path.join(config["analysis_name"]+os.sep+config["merge_qc"], "{sample_merged}_%s_stats.txt"%genomeV),
    output:
        os.path.join(config["analysis_name"]+os.sep+config["merge_qc"], "{sample_merged}_%s_multiqc.html"%genomeV),
    params:
        extra="",
    log:
        os.path.join(config["analysis_name"], "logs/07_merge/{sample_merged}_%s_multiqc.txt"%genomeV),
    shell:
        """
            mkdir -p $(dirname {output})
            multiqc --force {params.extra} -n $(basename {output}) -o $(dirname {output}) {input} > {log} 2>&1
        """