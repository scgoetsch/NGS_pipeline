if config["concatenate_fastq"]:
    read_folder = config["reads_concat"]
else:
    read_folder = config["reads"]

ext_aligner=["_R1.fastq.gz", "_R2.fastq.gz"]


def concat_inputs_for_sample(wildcards):
    prefixes = concat_map[wildcards.sample]
    if config["single_paired_end"] == "paired":
        inputs = []
        for prefix in prefixes:
            inputs.extend([
                os.path.join(config["analysis_name"] + os.sep + config["reads"], f"{prefix}_R1.fastq.gz"),
                os.path.join(config["analysis_name"] + os.sep + config["reads"], f"{prefix}_R2.fastq.gz"),
            ])
        return inputs
    return [
        os.path.join(config["analysis_name"] + os.sep + config["reads"], f"{prefix}.fastq.gz")
        for prefix in prefixes
    ]


def merge_inputs_for_sample(wildcards):
    return [
        os.path.join(config["analysis_name"] + os.sep + config["duplicates"], f"{sample}_{genomeV}.bam")
        for sample in merge_map[wildcards.sample_merged]
    ]


rule move_fastq:
    input:
        r1=os.path.join(config["fastq_home_dir"], "{sample_or}.fastq.gz"),
    output:
        r1=os.path.join(config["analysis_name"]+os.sep+config["reads"], "{sample_or}.fastq.gz"),
    params:
        config_name=config["analysis_name"],
    log:
        os.path.join(config["analysis_name"], "logs/01_move_fastq/{sample_or}.txt"),
    shell:
        """
            cp {input.r1} {output.r1}
            echo Copy DONE! >> {log}
        """


rule concatenating:
    input:
        concat_inputs_for_sample,
    output:
        f=os.path.join(config["analysis_name"]+os.sep+config["reads_concat"], "{sample}.txt"),
    params:
        folderin=config["analysis_name"]+os.sep+config["reads"],
        folderout=config["analysis_name"]+os.sep+config["reads_concat"],
        end=config["single_paired_end"],
        concat=config["concatenate_fastq"],
    log:
        os.path.join(config["analysis_name"], "logs/01_move_fastq/{sample}_concat.txt"),
    run:
        if params.concat:
            import subprocess

            if params.end == 'paired':
                infastq1 = [path for path in input if path.endswith("_R1.fastq.gz")]
                infastq2 = [path for path in input if path.endswith("_R2.fastq.gz")]
                outfasq1 = params.folderout+os.sep+wildcards.sample+"_R1.fastq.gz"
                outfasq2 = params.folderout+os.sep+wildcards.sample+"_R2.fastq.gz"

                subprocess.run(f"cat {' '.join(infastq1)} > {outfasq1}", shell=True, check=True)
                subprocess.run(f"cat {' '.join(infastq2)} > {outfasq2}", shell=True, check=True)
            else:
                infastq = list(input)
                outfasq = params.folderout+os.sep+wildcards.sample+".fastq.gz"
                subprocess.run(f"cat {' '.join(infastq)} > {outfasq}", shell=True, check=True)

            with open(output.f, 'w') as nfile:
                nfile.write("Concatenation Done!")
        else:
            with open(output.f, 'w') as nfile:
                nfile.write("Skip concatenation!")


rule trimming:
    input:
        c=os.path.join(config["analysis_name"]+os.sep+config["reads_concat"], "{sample}.txt"),
        # f=expand(os.path.join(config["analysis_name"]+os.sep+read_folder, "{samp}.fastq.gz"), samp=list(origin_fastq_conact)),
    output:
        os.path.join(config["analysis_name"]+os.sep+config["trimming_qc"], "{sample}_qc.txt"),
    params:
        config_name=config["analysis_name"],
        cut_bool=config["cutadapters_bool"],
        end=config["single_paired_end"],
        out_folder=config["analysis_name"]+os.sep+config["trimming"],
        in_fastq=os.path.join(config["analysis_name"]+os.sep+read_folder, "{sample}"),
        out_fastq=os.path.join(config["analysis_name"]+os.sep+config["trimming"], "{sample}"),
        trimming_PE_extra=config["trimming_PE_extra"],
        trimming_SE_extra=config["trimming_SE_extra"],
        threads=4,
        info_trim_file=config["analysis_name"]+os.sep+config["trimming_qc"]+os.sep+"Untrimmed.txt",
    log:
        os.path.join(config["analysis_name"], "logs/02_trimming/{sample}.txt"),
    shell:
        """
            if [ {params.cut_bool} == "True" ]
            then
                mkdir -p {params.out_folder}
                if [ {params.end} == "paired" ]
                then
                    trimmomatic PE -threads {params.threads} -trimlog {log} {params.in_fastq}_R1.fastq.gz {params.in_fastq}_R2.fastq.gz {params.out_fastq}_R1.fastq.gz {params.out_fastq}_R1_orphan.fastq.gz {params.out_fastq}_R2.fastq.gz {params.out_fastq}_R2_orphan.fastq.gz {params.trimming_PE_extra}
                    echo trimming PE DONE! >> {output}
                else
                    trimmomatic SE -threads {params.threads} -trimlog {log} {params.in_fastq}.fastq.gz {params.out_fastq}.fastq.gz {params.trimming_SE_extra}
                    echo trimming SE DONE! >> {output}
                fi
            else
                mkdir -p {params.out_folder}
                if [ {params.end} == "paired" ]
                then
                    cp {params.in_fastq}_R1.fastq.gz {params.out_fastq}_R1.fastq.gz
                    cp {params.in_fastq}_R2.fastq.gz {params.out_fastq}_R2.fastq.gz
                    echo Skip trimming PE! >> {output}
                else
                    cp {params.in_fastq}.fastq.gz {params.out_fastq}.fastq.gz
                    echo These fastq files have not been trimmed!!! >> {params.info_trim_file}
                    echo Skip trimming SE! >> {output}
                fi
            fi
        """


rule aligner:
    input:
        os.path.join(config["analysis_name"]+os.sep+config["trimming_qc"], "{sample}_qc.txt"),
    output:
        os.path.join(config["analysis_name"]+os.sep+config["aligner"], "{sample}_%s.bam"%genomeV),
    params:
        config_name=config["analysis_name"],
        sample_p=expand(config["analysis_name"]+os.sep+os.path.join(config["trimming"], "{samples}"), samples=["{sample}%s"%extB for extB in ext_aligner]),
        sample_s=expand(config["analysis_name"]+os.sep+os.path.join(config["trimming"], "{samples}"), samples=["{sample}.fastq.gz"]),
        aligner_algorithm=config['aligner_algorithm'],
        idx=config["aligner_dir"],
        out_folder=config["analysis_name"]+os.sep+config["aligner"],
        threads="4",
        end=config["single_paired_end"],
        extra=config["aligner_extra"],
    log:
        os.path.join(config["analysis_name"], "logs/03_aligner/{sample}_%s.txt"%genomeV),
    shell:
        """
            mkdir -p {params.out_folder}

            if [ {params.aligner_algorithm} == "bowtie2" ]
            then

                if [ {params.end} == "paired" ]
                then
                    (bowtie2 --threads {params.threads} -1 {params.sample_p[0]} -2 {params.sample_p[1]} -x {params.idx} {params.extra} | samtools view -o {output} --output-fmt BAM -) > {log}
                else
                    (bowtie2 --threads {params.threads} -U {params.sample_s} -x {params.idx} {params.extra} | samtools view -o {output} --output-fmt BAM -) > {log}
                fi
            else
                if [ {params.end} == "paired" ]
                then
                    bwa-mem2 mem -t {params.threads} {params.idx} {params.sample_p[0]} {params.sample_p[1]} | samtools view -@ {params.threads} -bh > {output}
                    echo bwa-mem2 Done! >> {log}
                else
                    bwa-mem2 mem -t {params.threads} {params.idx} {params.sample_s} | samtools view -@ {params.threads} -bh > {output}
                    echo bwa-mem2 Done! >> {log}
                fi
            fi
            
        """


rule filtering:
    input:
        os.path.join(config["analysis_name"]+os.sep+config["aligner"], "{sample}_%s.bam"%genomeV),
    output:
        os.path.join(config["analysis_name"]+os.sep+config["filtering"], "{sample}_%s.bam"%genomeV),
    log:
        os.path.join(config["analysis_name"], "logs/04_filtering/{sample}_%s.txt"%genomeV),
    params:
        config_name=config["analysis_name"],
        extra=config["filtering_extra"],
        end=config["single_paired_end"],
        filtering_folder=config["analysis_name"]+os.sep+config["filtering"],
        info_filter_file=config["analysis_name"]+os.sep+config["filtering"]+os.sep+"Unfiltered.txt",
    shell:
        """
            if [ {params.end} == "paired" ]
            then
                samtools view -o {output} {params.extra} {input}
            else
                mkdir -p {params.filtering_folder}
                echo These bam files have not been filtered \(single-end\)!!! >> {params.info_filter_file}
                cp {input} {output}
            fi
        """

        
rule samtools_sort:
    input:
        os.path.join(config["analysis_name"]+os.sep+config["filtering"], "{sample}_%s.bam"%genomeV),
    output:
        os.path.join(config["analysis_name"]+os.sep+config["sorted"], "{sample}_%s.bam"%genomeV),
    log:
        os.path.join(config["analysis_name"], "logs/05_samtools_sort/{sample}_%s.txt"%genomeV),
    params:
        config_name=config["analysis_name"],
        extra=config["samtools_sort_extra"],
    threads: 8
    shell:
        """
            mkdir -p $(dirname {output})
            samtools sort {params.extra} -@ {threads} -o {output} {input} > {log} 2>&1
        """
        

rule mark_duplicates:
    input:
        os.path.join(config["analysis_name"]+os.sep+config["sorted"], "{sample}_%s.bam"%genomeV),
    output:
        bam=os.path.join(config["analysis_name"]+os.sep+config["duplicates"], "{sample}_%s.bam"%genomeV),
        metrics=os.path.join(config["analysis_name"]+os.sep+config["duplicates_qc"], "{sample}_%s_metrics.txt"%genomeV),
    log:
        os.path.join(config["analysis_name"], "logs/06_mark_duplicates/{sample}_%s.txt"%genomeV),
    params:
        config_name=config["analysis_name"],
        extra=config["mark_duplicates_extra"],
    resources:
        mem_mb=1024,
    shell:
        """
            mkdir -p $(dirname {output.bam}) $(dirname {output.metrics}) $(dirname {log})
            tmp_rg="{output.bam}.rg_tmp.bam"
            trap 'rm -f "$tmp_rg"' EXIT
            samtools addreplacerg \
                -r 'ID:{wildcards.sample}' \
                -r 'SM:{wildcards.sample}' \
                -r 'LB:{wildcards.sample}' \
                -r 'PL:ILLUMINA' \
                -o "$tmp_rg" {input}
            picard MarkDuplicates \
                {params.extra} \
                --INPUT "$tmp_rg" \
                --OUTPUT {output.bam} \
                --METRICS_FILE {output.metrics} \
                > {log} 2>&1
        """


rule merge_bam:
    input:
        bam=merge_inputs_for_sample,
    output:
        os.path.join(config["analysis_name"]+os.sep+config["merge"], "{sample_merged}_%s.bam"%genomeV),
    params:
        config_name=config["analysis_name"],
        folder_duplicates=config["analysis_name"]+os.sep+config["duplicates"],
        folder_merge_bams=config["analysis_name"]+os.sep+config["merge"],
        merge_bams=config["merge_bams"],
        info_merge_file=config["analysis_name"]+os.sep+config["merge"]+os.sep+"Unmerged.txt",
    log:
        os.path.join(config["analysis_name"], "logs/07_merge/01_merge{sample_merged}_%s.txt"%genomeV),
    shell:
        """
            mkdir -p {params.folder_merge_bams}
            if [ "{params.merge_bams}" == "True" ]
            then
                samtools merge {output} {input.bam}
            else
                echo These bam files have not been merged \(as stated in the config file\)!!! >> {params.info_merge_file}
                cp {input.bam} {output}
            fi
        """      
                
        
rule samtools_index:
    input:
        os.path.join(config["analysis_name"]+os.sep+config["merge"], "{sample_merged}_%s.bam"%genomeV),  
    output:
        os.path.join(config["analysis_name"]+os.sep+config["merge"], "{sample_merged}_%s.bam.bai"%genomeV),        
    log:
        os.path.join(config["analysis_name"], "logs/07_merge/02_samtools_index/{sample_merged}_%s.txt"%genomeV),
    params:
        config_name=config["analysis_name"],
        extra=config["samtools_index_extra"], 
    threads: 4
    shell:
        """
            samtools index {params.extra} -@ {threads} {input} {output} > {log} 2>&1
        """
        
        
rule bam_coverage:
    input:
        bam=os.path.join(config["analysis_name"]+os.sep+config["merge"], "{sample_merged}_%s.bam"%genomeV),
        index=os.path.join(config["analysis_name"]+os.sep+config["merge"], "{sample_merged}_%s.bam.bai"%genomeV),      
    output:
        os.path.join(config["analysis_name"]+os.sep+config["bam_coverage"], "{sample_merged}_%s.bw"%genomeV),
    params:
        config_name=config["analysis_name"],
        extra1=config["bam_coverage_params1"],
        extra2=config["bam_coverage_params2"], 
        end=config["single_paired_end"],
    log:
        os.path.join(config["analysis_name"], "logs/08_bam_coverage/{sample_merged}_%s.txt"%genomeV),
    shell:
        """
            if [ {params.end} == "paired" ]
            then
                bamCoverage -b {input.bam} -o {output} {params.extra1} {params.extra2}
            else
                bamCoverage -b {input.bam} -o {output} {params.extra1}
            fi
        """
        
        
rule peak_caller:
    input:
        bw=os.path.join(config["analysis_name"]+os.sep+config["bam_coverage"], "{sample_merged}_%s.bw"%genomeV),
        bam=os.path.join(config["analysis_name"]+os.sep+config["merge"], "{sample_merged}_%s.bam"%genomeV),
        bai=os.path.join(config["analysis_name"]+os.sep+config["merge"], "{sample_merged}_%s.bam.bai"%genomeV),
    output:
        os.path.join(config["analysis_name"]+os.sep+config["peaks_log"], "{sample_merged}_%s.txt"%genomeV),
    params:
        peak_caller=config["peak_caller"],
        macs2_extra1= config["macs2_extra1"],
        macs2_extra2= config["macs2_extra2"],
        config_name=config["analysis_name"],
        folder=config["analysis_name"]+os.sep+config["peaks"],
        bam_coverage=config["bam_coverage_params1"],
    shell:
        """
            if [ "{params.peak_caller}" == "lanceotron" ]
            then
                if [ "{params.bam_coverage}" == "-bs 1 --normalizeUsing RPKM" ]
                then
                    lanceotron callPeaks {input.bw} -f {params.folder}
                    echo {wildcards.sample_merged} lanceotron peak calling DONE! >> {output}
                else
                    echo lanceotron peak calling, skipped because -bs 1 --normalizeUsing RPKM are different from default settings >> {output}
                fi
            else
                {params.peak_caller} callpeak {params.macs2_extra1} --treatment {input.bam} {params.macs2_extra2} --outdir {params.folder} --name {wildcards.sample_merged}
                echo {wildcards.sample_merged} {params.peak_caller} peak calling DONE! >> {output}
            fi
        """  
