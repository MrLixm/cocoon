# assume PWD is the parent directory
repo_root="`realpath ../`"
profile_result_dir="./results/"
[[ ! -d "$profile_result_dir" ]] && mkdir $profile_result_dir

current_date="`date +%Y%m%d_%H%M%S`"
export PYTHONPATH="$repo_root"

for script_path in "$PWD"/*.py
do
  script_name=$(basename $script_path .py)
  plot_dir="$profile_result_dir/$script_name/"
  [[ ! -d "$plot_dir" ]] && mkdir $plot_dir
  plot_path="$plot_dir$script_name-$current_date.png"
  script_path_platform=$(cygpath -m $script_path)

  echo "==[ about to profile $script_path_platform ..."
  psrecord "python $script_path_platform" --plot $plot_path --include-children
  echo "]== profiling finished, result at $plot_path"
done