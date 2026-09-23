#!/bin/bash
#SBATCH -n 72
#SBATCH --constraint icelake
#SBATCH --qos bbdefault
#SBATCH -A scanlodo-jm-green-h2
#SBATCH -t 24:00:0
#SBATCH --nodes 2

module purge
module load bluebear
module load bear-apps/2022a
module load VASP/6.3.2-foss-2022a

mpirun -np ${SLURM_NTASKS} vasp_std

