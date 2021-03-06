[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3822314.svg)](https://doi.org/10.5281/zenodo.3822314)

# daily_GRF

Repo with code to predict ground reaction forces (GRF) based on daily living raw acceleration data using the methods describe by [Veras et al (2020)](https://link.springer.com/article/10.1007/s00198-020-05295-2).

In the [code](code/) directory there are 5 scripts, each for a part of the data analysis process. The shell script [process.sh](process.sh) in the main directory controls the execution of these 5 parts.

---

**[Part 1](code/part1_gt3x_to_txt.R)**

R code. Reads raw acceleration data in a .gt3x file format using the `read.gt3x` [package](https://github.com/THLfi/read.gt3x) and writes it in a .txt file format using the `readr` [package](https://readr.tidyverse.org).


**[Part 2](code/part2_mark_wear_time.R)**

R code. Uses de `PhysicalActivity` [package](https://CRAN.R-project.org/package=PhysicalActivity) to mark the wear and non-wear times from an .agd file with 60 seconds epoch. The wear time recognition algorithm is set to use the vector magnitude and have a 90 minutes frame with 2 minutes of allowance.

**[Part 3](code/part3_process_raw_acc.py)**

Python code. It first reads the raw acceleration .txt file generated by the [Part 1](code/part1_gt3x_to_txt.R) into a `pandas.DataFrame`, puts each acceleration axis into a `numpy.ndarray` and filters it using the `scipy.signal` [module](https://docs.scipy.org/doc/scipy/reference/signal.html). The filter used is a Butterworth fourth-order low-pass filter, with 20 Hz cutoff frequency. Then, it selects only the wear time detected by [Part 2](code/part2_mark_wear_time.R) and find the acceleration peaks, again using the `scipy.signal` [module](https://docs.scipy.org/doc/scipy/reference/signal.html). The minimum height criteria for the peak detection is 1.2*g* and the minimum distance is 0.4 seconds.

**[Part 4](code/part4_compute_GRF.py)**

Python code. It reads the acceleration peaks detected in [Part 3](code/part3_process_raw_acc.py) and uses them to apply the GRF prediction equations developed by [Veras et al (2020)](https://link.springer.com/article/10.1007/s00198-020-05295-2). Then it computes some summary statistics regarding the GRF values, put them into a `pandas.DataFrame` and writes it into a .csv file.

**[Part 5](code/part5_clean_df.R)**

R code. Simply cleans the summary data created in [Part 4](code/part4_compute_GRF.py) using [`dplyr`](https://dplyr.tidyverse.org) tools writes it into two separate .csv data files.

---

**TODO:**

-  Improve raw accelerometer data writing and reading.
-  Allow to use with different epoch lengths and sample frequencies.
	+  Automatically detect these parameters.
- Allow to select which statistics will be computed.
- Create a data dictionary.
