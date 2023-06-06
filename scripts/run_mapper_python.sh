#!/bin/bash
### sbatch config parameters must start with #SBATCH and must precede any other command. to ignore just add another # - like so ##SBATCH
#SBATCH --partition main ### specify partition name where to run a job
#SBATCH --time 7-00:00:00 ### limit the time of job running. Format: D-H:MM:SS
#SBATCH --job-name run_mapper_python ### name of the job. replace my_job with your desired job name
#SBATCH --output run_mapper_python.out ### output log for running job - %J is the job number variable
#SBATCH --mail-user=tomya@post.bgu.ac.il ### users email for sending job status notifications ñ replace with yours
#SBATCH --mail-type=BEGIN,END,FAIL ### conditions when to send the email. ALL,BEGIN,END,FAIL, REQUEU, NONE
#SBATCH --mem=500G ### total amount of RAM // 500
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32 ##. // max 128

### Start you code below ####
module load anaconda ### load anaconda module
source activate bppy_model_checking ### activating Conda environment. Environment must be configured before running the job
cd ~/repos/BPpyModelChecker/ || exit
ulimit -s unlimited
#options = ()
options=(

"hot_cold 30 1" "hot_cold 60 1" "hot_cold 90 1"
"hot_cold 30 2" "hot_cold 60 2" "hot_cold 90 2"
"hot_cold 30 3" "hot_cold 60 3" "hot_cold 90 3"

"dining_philosophers 3" "dining_philosophers 6" "dining_philosophers 9" "dining_philosophers 12" "dining_philosophers 15"

"ttt 2 2" "ttt 3 3" "ttt 4 4"
)

for option in "${options[@]}"; do
  echo "$option"
  timeout 600m python run_mapper.py $option
done