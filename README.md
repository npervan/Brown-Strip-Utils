# Brown-Strip-Utils

To run for strip/interstrip measurements use multi_sensor_plotter.py

Exact method to call depends on filepaths. I have set up so multi_sensor_plotter.py and folder with batch number are in Brow-Strip-Utils directory. Within the batch folder I create a directory called strip and one called interstrip and put the text files inside. Then code is called as follows:

```
python3 multi_sensor_plotter.py -i 42257/strip -o 42257/strip_plot -a 42257/strip_avgs_42257
python3 multi_sensor_plotter.py -i 42257/interstrip -o 42257/interstrip_plot -a 42257/interstrip_avgs_42257
```

When dealing with files that have reruns I replace the rerun strip with the newest version and keep an original file with original run plus reruns directly in the batch directory. The original files also remain on fileway.

## Possible Improvements
When restarting labview the number of measurements for each type is reset to a default (i.e. rpoly for strip and interstrip resistance for interstrip). If two files in one batch have a different number of columns the code will fail.
