#!/bin/bash
### sbatch config parameters must start with #SBATCH and must precede any other command. to ignore just add another # - like so ##SBATCH
#SBATCH --partition main ### specify partition name where to run a job
#SBATCH --time 7-00:00:00 ### limit the time of job running. Format: D-H:MM:SS
#SBATCH --job-name run_all ### name of the job. replace my_job with your desired job name
#SBATCH --output run_all_bppy.out ### output log for running job - %J is the job number variable
#SBATCH --mail-user=tomya@post.bgu.ac.il ### users email for sending job status notifications ñ replace with yours
#SBATCH --mail-type=BEGIN,END,FAIL ### conditions when to send the email. ALL,BEGIN,END,FAIL, REQUEU, NONE
#SBATCH --mem=16G ### total amount of RAM // 500
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32 ##. // max 128

### Start you code below ####
module load anaconda ### load anaconda module
source activate bppy_model_checking ### activating Conda environment. Environment must be configured before running the job
cd ~/repos/BPpyModelChecker/ || exit
#option = ()
options=(
"hot_cold1 30 1" "hot_cold1 60 1" "hot_cold1 90 1"
"hot_cold1 30 2" "hot_cold1 60 2" "hot_cold1 90 2"
"hot_cold1 30 3" "hot_cold1 60 3" "hot_cold1 90 3"
"hot_cold2 30 1" "hot_cold2 60 1" "hot_cold2 90 1"
"hot_cold2 30 2" "hot_cold2 60 2" "hot_cold2 90 2"
"hot_cold2 30 3" "hot_cold2 60 3" "hot_cold2 90 3"

"dining_philosophers1 2" "dining_philosophers1 3" "dining_philosophers1 4" "dining_philosophers1 5"
"dining_philosophers2 2" "dining_philosophers2 3" "dining_philosophers2 4" "dining_philosophers2 5"

"ttt1 3 3" "ttt1 4 4" "ttt1 5 5"
"ttt2 3 3" "ttt2 4 4" "ttt2 5 5"
)
for option in "${options[@]}"; do
  echo "$option"
  timeout 30m /usr/bin/time -v python main.py $option
done