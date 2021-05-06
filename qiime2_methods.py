#!/usr/local/env python3

import os
import pathlib
import subprocess
from concurrent import futures


class Qiime2Methods(object):

    @staticmethod
    def make_folder(folder):
        """
        Create output folder.
        :param folder: string. Output folder path.
        :return:
        """
        # Will create parent directories if don't exist and will not return error if already exists
        pathlib.Path(folder).mkdir(parents=True, exist_ok=True)

    @staticmethod
    def list_fastq(my_path):
        """
        Walk input directory and list all the fastq files. Accepted file extensions are '.fastq', '.fastq.gz',
        '.fq' and '.fq.gz'.
        :param my_path: string. Input folder path
        :return: list of strings. Fastq files in input folder
        """
        # Create empty list to hold the file paths
        fastq_list = list()
        # Walk the input directory recursively and look for fastq files
        for root, directories, filenames in os.walk(my_path):
            for filename in filenames:
                absolute_path = os.path.join(root, filename)
                if os.path.isfile(absolute_path) and filename.endswith(('.fastq', '.fastq.gz', '.fq', '.fq.gz')):
                    fastq_list.append(absolute_path)  # Add fastq file path to the list
        return fastq_list

    @staticmethod
    def rc_fastq(input_fastq, output_fastq):
        """

        :param input_fastq:
        :param output_fastq:
        :return:
        """
        cmd = ['reformat.sh',
               'ow=t',
               'rcomp=t',
               'in={}'.format(input_fastq),
               'out={}'.format(output_fastq)]
        subprocess.run(cmd)

    @staticmethod
    def rc_fastq_parallel(fastq_list, output_folder, cpu):
        with futures.ThreadPoolExecutor(max_workers=int(cpu / 4)) as executor:
            args = ((fastq, output_folder, int(cpu / 4)) for fastq in fastq_list)
            for results in executor.map(lambda p: Qiime2Methods.extract_its_se(*p), args):  # (*p) does the unpacking part
                pass

    @staticmethod
    def extract_its_se(fastq_file, output_folder, log_folder, cpu):
        """
        Extract Fungi ITS1 sequence from fastq files. Use ITSxpress program.
        :param fastq_file: string. Fastq file path
        :param output_folder: string. Path of output folder.
        :param cpu: int. number of CPU to use.
        :return:
        """
        cmd = ['itsxpress',
               '--threads', str(cpu),
               '--single_end',
               '--fastq', fastq_file,
               '--region', 'ITS1',
               '--taxa', 'Fungi',
               '--cluster_id', str(0.99),
               '--outfile', output_folder + '/' + os.path.basename(fastq_file),
               '--log',  log_folder + '/' + os.path.basename(fastq_file).split('_')[0] + '.log',
               '--threads', str(cpu)]
        subprocess.run(cmd)

    @staticmethod
    def extract_its_se_parallel(fastq_list, output_folder, log_folder, cpu):
        """
        Run "extract_its" in parallel using 4 cores per instance.
        :param fastq_list: string. A list of fastq file paths.
        :param output_folder: sting. Path of output folder
        :param cpu: int. Number of cpu to use.
        :return:
        """
        with futures.ThreadPoolExecutor(max_workers=int(cpu / 4)) as executor:
            args = ((fastq, output_folder, log_folder, int(cpu / 4)) for fastq in fastq_list)
            for results in executor.map(lambda p: Qiime2Methods.extract_its_se(*p), args):  # (*p) does the unpacking part
                pass

    @staticmethod
    def extract_its_pe(fastq_r1, fastq_r2, output_folder, log_folder, cpu):
        """
        Extract Fungi ITS1 sequence from fastq files. Use ITSxpress program.
        :param fastq_r1: string. Fastq file path
        :param fastq_r2: string. Fastq file path
        :param output_folder: string. Path of output folder.
        :param log_folder:
        :param cpu: int. number of CPU to use.
        :return:
        """
        cmd = ['itsxpress',
               '--threads', str(cpu),
               '--fastq', fastq_r1,
               '--fastq2', fastq_r2,
               '--region', 'ITS1',
               '--taxa', 'Fungi',
               '--cluster_id', str(0.99),
               '--outfile', output_folder + '/' + os.path.basename(fastq_r1),
               '--outfile2', output_folder + '/' + os.path.basename(fastq_r2),
               '--log',  log_folder + '/' + os.path.basename(fastq_r1).split('_')[0] + '.log',
               '--threads', str(cpu)]
        subprocess.run(cmd)

    @staticmethod
    def extract_its_pe_parallel(sample_dict, output_folder, log_folder, cpu):
        """
        Run "extract_its" in parallel using 4 cores per instance.
        :param sample_dict: string. A dictionary of fastq file paths.
        :param output_folder: sting. Path of output folder
        :param cpu: int. Number of cpu to use.
        :return:
        """
        with futures.ThreadPoolExecutor(max_workers=int(cpu / 4)) as executor:
            args = ((fastq_list[0], fastq_list[1], output_folder, log_folder, int(cpu / 4))
                    for sample, fastq_list in sample_dict.items())
            for results in executor.map(lambda p: Qiime2Methods.extract_its_pe(*p), args):  # (*p) unpacks arguments
                pass

    @staticmethod
    def fix_fastq_se(fastq_file):
        """
        Remove empty entries from a fastq file. Overwrites the input file with the output file.
        :param fastq_file: string. Path of a fastq file, gzipped or not.
        :return:
        """
        cmd = ['python', 'remove_empty_fastq_entries.py',
               '-f', fastq_file]
        subprocess.run(cmd)

    @staticmethod
    def fix_fastq_se_parallel(fastq_list, cpu):
        """
        Run "fix_fastq" in parallel using all the threads, one file per thread
        :param fastq_list: string. list of fastq file paths
        :param cpu: int. number of CPU to use
        :return:
        """
        with futures.ThreadPoolExecutor(max_workers=cpu) as executor:
            args = (fastq for fastq in fastq_list)
            for results in executor.map(Qiime2Methods.fix_fastq_se, args):
                pass

    @staticmethod
    def fix_fastq_pe(fastq_r1, fastq_r2):
        """
        Remove empty entries from a fastq file. Have to keep R1 and R2 synchronized.
        Overwrites the input file with the output file.
        :param fastq_r1: string. Path of a fastq R1 file, gzipped or not.
        :param fastq_r2: string. Path of a fastq R2 file, gzipped or not.
        :return:
        """
        cmd = ['python', 'remove_empty_fastq_entries.py',
               '-f', fastq_r1,
               '-f2', fastq_r2]
        subprocess.run(cmd)

    @staticmethod
    def fix_fastq_pe_parallel(sample_dict, cpu):
        """
        Run "fix_fastq" in parallel using all the threads, one file per thread
        :param sample_dict: string. Dictionary of fastq file paths
        :param cpu: int. number of CPU to use
        :return:
        """
        with futures.ThreadPoolExecutor(max_workers=cpu) as executor:
            args = ((fastq_list[0], fastq_list[1]) for sample, fastq_list in sample_dict.items())
            for results in executor.map(lambda p: Qiime2Methods.fix_fastq_pe(*p), args):  # (*p) unpacks arguments
                pass

    @staticmethod
    def qiime2_import_fastq_se(fastq_folder, reads_qza):
        """
        Import single-end fastq files
        https://docs.qiime2.org/2020.8/tutorials/importing/
        :param fastq_folder:
        :param reads_qza:
        :return:
        """
        cmd = ['qiime', 'tools', 'import',
               '--type', 'SampleData[SequencesWithQuality]',
               '--input-format', 'CasavaOneEightSingleLanePerSampleDirFmt',  # For demultiplexed single end fastq
               '--input-path', fastq_folder,
               '--output-path', reads_qza]
        subprocess.run(cmd)

    @staticmethod
    def qiime2_import_fastq_pe(fastq_folder, reads_qza):
        """
        Import paired-end fastq files
        https://docs.qiime2.org/2020.8/tutorials/importing/
        :param fastq_folder:
        :param reads_qza:
        :return:
        """
        cmd = ['qiime', 'tools', 'import',
               '--type', 'SampleData[PairedEndSequencesWithQuality]',
               '--input-format', 'CasavaOneEightSingleLanePerSampleDirFmt',  # For demultiplexed paired-end fastq
               '--input-path', fastq_folder,
               '--output-path', reads_qza]
        subprocess.run(cmd)

    @staticmethod
    def qiime2_demux_summary(reads_qza, output_qzv):
        """
        Make summary of samples
        Subsample 10,000 reads by default, only use 1000 instead (faster)
        :param reads_qza:
        :param output_qzv:
        :return:
        """
        cmd = ['qiime', 'demux', 'summarize',
               '--p-n', str(1000),
               '--i-data', reads_qza,
               '--o-visualization', output_qzv]
        subprocess.run(cmd)

    @staticmethod
    def qiime2_dada2_denoise_single(reads_qza, repseq_qza, table_qza, stats_qza):
        """
        Denoise single-end reads with DADA2
        :param reads_qza:
        :param repseq_qza:
        :param table_qza:
        :param stats_qza:
        :return:
        """
        cmd = ['qiime', 'dada2', 'denoise-single',
               '--p-n-threads', str(0),
               '--p-trim-left', str(0),  # No trimming
               '--p-trunc-len', str(0),  # No trimming
               '--i-demultiplexed-seqs', reads_qza,
               '--o-representative-sequences', repseq_qza,
               '--o-table', table_qza,
               '--o-denoising-stats', stats_qza]
        subprocess.run(cmd)

    @staticmethod
    def qiime2_dada2_denoise_paired(reads_qza, repseq_qza, table_qza, stats_qza):
        """
        Denoise paired-end reads with DADA2
        :param reads_qza:
        :param repseq_qza:
        :param table_qza:
        :param stats_qza:
        :return:
        """
        cmd = ['qiime', 'dada2', 'denoise-paired',
               '--p-n-threads', str(0),
               '--p-trim-left-f', str(0),  # No trimming
               '--p-trim-left-r', str(0),  # No trimming
               '--p-trunc-len-f', str(0),  # No trimming
               '--p-trunc-len-r', str(0),  # No trimming
               '--i-demultiplexed-seqs', reads_qza,
               '--o-representative-sequences', repseq_qza,
               '--o-table', table_qza,
               '--o-denoising-stats', stats_qza]
        subprocess.run(cmd)

    @staticmethod
    def qiime2_metadata_tabulate(stats_qza, stats_qzv):
        """

        :param stats_qza:
        :param stats_qzv:
        :return:
        """
        cmd = ['qiime', 'metadata', 'tabulate',
               '--m-input-file',  stats_qza,
               '--o-visualization',  stats_qzv]
        subprocess.run(cmd)

    @staticmethod
    def qiime2_export(qza, output_folder):
        """
        Export biom table
        :param qza: string. QIIME2 table
        :param output_folder: sting. Output folder
        :return:
        """
        cmd = ['qiime', 'tools', 'export',
               '--input-path',  qza,
               '--output-path', output_folder]  # this is a folder
        subprocess.run(cmd)

    @staticmethod
    def qiime2_sample_summarize(metadata_file, table_qza, table_qzv):
        """

        :param metadata_file:
        :param table_qza:
        :param table_qzv:
        :return:
        """
        cmd = ['qiime', 'feature-table', 'summarize',
               '--m-sample-metadata-file', metadata_file,
               '--i-table', table_qza,
               '--o-visualization',  table_qzv]
        subprocess.run(cmd)

    @staticmethod
    def qiime2_seq_sumamry(repseqs_qza, repseqs_qzv):
        """

        :param repseqs_qza:
        :param repseqs_qzv:
        :return:
        """
        cmd = ['qiime', 'feature-table', 'tabulate-seqs',
               '--i-data', repseqs_qza,
               '--o-visualization',  repseqs_qzv]
        subprocess.run(cmd)

    @staticmethod
    def qiime2_phylogeny(repseqs_qza, align_repseqs_qza, masked_align_repseqs_qza, unrooted_tree_qza, rooted_tree_qza):
        """

        :param repseqs_qza:
        :param align_repseqs_qza:
        :param masked_align_repseqs_qza:
        :param unrooted_tree_qza:
        :param rooted_tree_qza:
        :return:
        """
        cmd = ['qiime', 'phylogeny', 'align-to-tree-mafft-fasttree',
               '--p-n-threads', 'auto',
               '--i-sequences', repseqs_qza,
               '--o-alignment', align_repseqs_qza,
               '--o-masked-alignment', masked_align_repseqs_qza,
               '--o-tree', unrooted_tree_qza,
               '--o-rooted-tree', rooted_tree_qza]
        subprocess.run(cmd)

    @staticmethod
    def qiime2_core_diversity(cpu, metadata_file, rooted_tree_qza, table_qza, output_folder):
        """
        Alpha and Beta analysis
        :param cpu:
        :param metadata_file:
        :param rooted_tree_qza:
        :param table_qza:
        :param output_folder:
        :return:
        """
        cmd = ['qiime', 'diversity', 'core-metrics-phylogenetic',
               '--p-n-jobs-or-threads', str(cpu),
               '--p-sampling-depth', str(1000),
               '--i-phylogeny', rooted_tree_qza,
               '--i-table', table_qza,
               '--m-metadata-file', metadata_file,
               '--output-dir', output_folder + '/core-metrics-results']

    @staticmethod
    def qiime2_rarefaction(metadata_file, rooted_tree_qza, table_qza, rare_qzv):
        """

        :param metadata_file:
        :param rooted_tree_qza:
        :param table_qza:
        :param rare_qzv:
        :return:
        """
        cmd = ['qiime', 'diversity', 'alpha-rarefaction',
               '--p-max-depth', str(4000),
               '--i-phylogeny', rooted_tree_qza,
               '--i-table', table_qza,
               '--m-metadata-file', metadata_file,
               '--o-visualization', rare_qzv]
        subprocess.run(cmd)

    @staticmethod
    def qiime2_classify(qiime2_classifier, repseqs_qza, taxonomy_qza):
        """
        Taxonomic analysis
        :param qiime2_classifier:
        :param repseqs_qza:
        :param taxonomy_qza:
        :return:
        """
        cmd = ['qiime', 'feature-classifier', 'classify-sklearn',
               '--p-n-jobs', str(-1),
               '--i-classifier', qiime2_classifier,
               '--i-reads', repseqs_qza,
               '--o-classification',  taxonomy_qza]
        subprocess.run(cmd)

    @staticmethod
    def change_taxonomy_file_header(input_taxo):
        """

        :param input_taxo:
        :return:
        """
        tmp = input_taxo + '.tmp'
        with open(tmp, 'w') as out_f:
            out_f.write('#OTUID\ttaxonomy\tconfidence\n')  # write new header
            with open(input_taxo, 'r') as in_f:
                next(in_f)  # skip header
                for line in in_f:
                    out_f.write(line)  # dump rest of file
        # overwrite original taxonomy file
        os.replace(tmp, input_taxo)

    @staticmethod
    def biom_add_metadata(input_biom, taxonomy_tsv, output_biom):
        """

        :param input_biom:
        :param taxonomy_tsv:
        :param output_biom:
        :return:
        """
        cmd = ['biom', 'add-metadata',
               '--sc-separated', 'taxonomy',
               '-i', input_biom,
               '--observation-metadata-fp', taxonomy_tsv,
               '-o', output_biom]
        subprocess.run(cmd)

    @staticmethod
    def biom_convert_taxo(input_biom_taxo, taxonomy_tsv, output_tsv_taxo):
        """

        :param input_biom_taxo:
        :param taxonomy_tsv:
        :param output_tsv_taxo:
        :return:
        """
        cmd = ['biom', 'convert',
               '--to-tsv',
               '--header-key', 'taxonomy',
               '-i', input_biom_taxo,
               '--observation-metadata-fp', taxonomy_tsv,
               '-o', output_tsv_taxo]
        subprocess.run(cmd)

    @staticmethod
    def qiime2_taxa_barplot(table_qza, taxonomy_qza, metadata_file, taxo_bar_plot_qzv):
        """

        :param table_qza:
        :param taxonomy_qza:
        :param metadata_file:
        :param taxo_bar_plot_qzv:
        :return:
        """
        cmd = ['qiime', 'taxa', 'barplot',
               '--i-table', table_qza,
               '--i-taxonomy', taxonomy_qza,
               '--m-metadata-file', metadata_file,
               '--o-visualization', taxo_bar_plot_qzv]
        subprocess.run(cmd)
