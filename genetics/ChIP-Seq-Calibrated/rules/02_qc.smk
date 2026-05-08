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
        
        
rule bowtie2_stats:
    input:
        bam=os.path.join(config["analysis_name"]+os.sep+config["bowtie2"], "{sample}.bam"),
    output:
        os.path.join(config["analysis_name"]+os.sep+config["bowtie2_qc"], "{sample}_stats.txt"),
    params:
        extra="",
    log:
        os.path.join(config["analysis_name"], "logs/03_bowtie2/{sample}_stats.txt"),
    shell:
        """
            mkdir -p $(dirname {output})
            samtools stats {params.extra} {input.bam} > {output} 2> {log}
        """

        
rule bowtie2_multiqc:
    input:
        os.path.join(config["analysis_name"]+os.sep+config["bowtie2_qc"], "{sample}_stats.txt"),
    output:
        os.path.join(config["analysis_name"]+os.sep+config["bowtie2_qc"], "{sample}_multiqc.html")
    params:
        extra="",
    log:
        os.path.join(config["analysis_name"], "logs/03_bowtie2/{sample}_multiqc.txt"),
    shell:
        """
            mkdir -p $(dirname {output})
            multiqc {params.extra} -n $(basename {output}) -o $(dirname {output}) {input} > {log} 2>&1
        """
        
        
rule sorted_dedup_stats:
    input:
        bam=os.path.join(config["analysis_name"]+os.sep+config["duplicates"], "{sample}_sorted_dedup.bam"),
    output:
        os.path.join(config["analysis_name"]+os.sep+config["duplicates_qc"], "{sample}_sorted_dedup_stats.txt"),
    params:
        extra="",
    log:
        os.path.join(config["analysis_name"], "logs/05_mark_duplicates/{sample}_stats.txt"),
    shell:
        """
            mkdir -p $(dirname {output})
            samtools stats {params.extra} {input.bam} > {output} 2> {log}
        """

        
rule sorted_dedup_multiqc:
    input:
        os.path.join(config["analysis_name"]+os.sep+config["duplicates_qc"], "{sample}_sorted_dedup_stats.txt"),
    output:
        os.path.join(config["analysis_name"]+os.sep+config["duplicates_qc"], "{sample}_sorted_dedup_multiqc.html")
    params:
        extra="",
    log:
        os.path.join(config["analysis_name"], "logs/05_mark_duplicates/{sample}_multiqc.txt"),
    shell:
        """
            mkdir -p $(dirname {output})
            multiqc {params.extra} -n $(basename {output}) -o $(dirname {output}) {input} > {log} 2>&1
        """