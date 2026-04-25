# Calibrated ChIP-seq

### Overview
This user-friendly pipeline is built using [Snakemake](https://snakemake.readthedocs.io/en/stable/).

This pipeline is built for the comparative analysis of ChIP-seq data across biological conditions through the utilisation of spike-in normalisation. The downsampling calculation utilised in this pipeline is based on the method published in [Fursova _et al._ Mol Cell (2019)](https://doi.org/10.1016/j.molcel.2019.03.024)   

```
                                                       1                   N(spike-in in Input)
                Downsampling factor = α x --------------------------  x  -----------------------
                                              N(spike-in in ChIP)           N(target in Input)


              Where:
 N(spike-in in ChIP)    Σ reads aligning to spike-in genome for each ChIP-seq sample.
N(spike-in in Input)    Σ reads aligning to spike-in genome in the corresponding input sample.
  N(target in Input)    Σ reads aligning to mouse genome in the corresponding input sample.
                  α     coefficient applied to all files normalised together so that the value of the largest downsampling factor equals 1.
```
***
:star:  For gold-standard calibrated ChIP-seq analysis, input control samples should be provided for each ChIP sample. :star:     

***

### Preliminary requirements 

#### 1. UpStreamPipeline set-up :hammer_and_wrench:

Follow the instructions on [UpStreamPipeline](https://github.com/Genome-Function-Initiative-Oxford/UpStreamPipeline) to set up the correct environment. 

#### 2. Catenated genome :dna: + :dna:

In order to align to the genome + spike-in genome simultaneously, create a catenated genome as follows.

i. Take the two genomes of interest and rename chromosomes so that thet include species: 
 
```
# TARGET GENOME
sed 's/>chr/>mm39_chr/g' /databank/igenomes/Mus_musculus/UCSC/mm39/Sequence/Bowtie2Index/genome.fa > ./mm39_genome.fa

# SPIKE-IN GENOME
sed 's/>chr/>dm6_chr/g' /databank/igenomes/Drosophila_melanogaster/UCSC/dm6/Sequence/Bowtie2Index/genome.fa > ./dm6_genome.fa
```

ii. Catenate these two genomes:

```
cat ./mm39_genome.fa ./dm6_genome.fa > catenated_mm39_dm6.fa &
```

ii. Then need to build bowtie2 index [See detailed instructions on Homer webpage](http://homer.ucsd.edu/homer/basicTutorial/mapping.html)

```bowtie2-build /path/catenated_mm39_dm6.fa mm39.dm6```


#### 3. Sample metadata

This pipeline now supports two input metadata formats:

1. **Modern sample sheet** via `sample_sheet` in `config/analysis.yaml`
2. **Legacy** `fastqfile_home_dir.txt`

The recommended modern sample sheet is TSV or CSV with the following columns:

- `chip_fastq_prefix` (required)
- `input_fastq_prefix` (required when `input_provided: true`)

Recommended examples:
- bundled example sample sheet: [`config/example.samples.tsv`](./config/example.samples.tsv)
- reusable dry-run fixture: [`../../tests/fixtures/chip-calibrated-basic/`](../../tests/fixtures/chip-calibrated-basic)

Example (`config/example.samples.tsv`):

```tsv
chip_fastq_prefix	input_fastq_prefix
H3K4me3_ChIP_HeLa_sample1	H3K4me3_input_HeLa_sample1
H3K4me3_ChIP_HeLa_sample2	H3K4me3_input_HeLa_sample2
```

Legacy mode still works via `fastqfile_home_dir.txt`, which should be tab-separated without headers:

- column 1: ChIP FASTQ prefix
- column 2: input FASTQ prefix (only when `input_provided: true`)

#### 4. Modify the config.yaml file

Detailed instructions are provided in the config.yaml file for editing the necessary parameters.
Boolean values may now be written as YAML booleans (`true` / `false`) or legacy strings (`"True"` / `"False"`).

A few key points:   
- Include the full path to the catenated genome bowtie2 build.
- Correctly assign the target and spike-in genome.
- Specify whether your fastq files are single- or paired-end

***

### Additional info:
This pipeline will run all the analyses in the ChIP-Seq snakemake folder, within the config.yaml you can specify where to move all the final analysis files to within your directory and if you would like to delete any intermediate files.

#### Output folders:
When running the pipeline, results, QCs, and logs folders will be automatically generated with all related outputs inside the output folder specified in the config.yaml file.

***
### How to run the calibrated ChIP pipeline
Option #1: run locally with Pixi from the repository root
```bash
pixi install -e chip-calibrated
PIXI_CORES=4 pixi run -e chip-calibrated chip-calibrated
```

Option #1a: reusable fixture dry-run from the repository root
```bash
pixi run -e chip-calibrated bash -lc 'cd genetics/ChIP-Seq-Calibrated && snakemake --configfile=../../tests/fixtures/chip-calibrated-basic/config.yaml -n all --cores 1'
```

Option #2: run locally with Snakemake
```bash
snakemake --configfile=config/analysis.yaml all --cores 4
```

Option #3: SLURM
Modify parameters of `submit.sh` (conda-based) or `submit.pixi.sh` (Pixi-based), then submit:
```bash
sbatch submit.pixi.sh
```
