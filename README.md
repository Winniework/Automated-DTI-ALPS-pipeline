[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
# Automated-DTI-ALPS-pipeline
This repo accompanies the manuscript "Cerebral Fluid Circulation Modulates Aging-induced Small Vessel Disease Burden and Cognitive Impairment".

Diffusion tensor image analysis along the perivascular space (DTI-ALPS) analysis relies on identifying association and projection fibers, and the method of placing 5 mm-diameter circular regions of interest (ROIs) has been proven to outperform existing automated mapping methods. However, unlike clear lesions, manual placement of ROIs lacks definite standards and changes according to different operators. Because the ROIs are confined to 5 mm circles, it is difficult to assure the accuracy of ROI registration based on whole-brain registration; thus, this method still requires manual adjustment, leading to the publication of a non-automated process. Therefore, we developed an automated analysis pipeline from inputting the original data to computing the final ALPS index.

## Methods
![](https://github.com/Winniework/Automated-DTI-ALPS-pipeline/blob/main/figure.jpg)

The DTI data of each participant were first preprocessed to obtain reoriented colored fractional anisotropy maps, where Dxx, Dyy, and Dzz represented diffusion along the x, y, and z axes, respectively, to improve reproducibility [Tatekawa et al., 2023]. The key step in automated APLS analysis was to place circular ROIs of 5 mm-diameter on the green and blue fiber bundles of the fractional anisotropy (FA) color map after preprocessing [Zhang et al., 2021]. Referring to the procedure of manual placement and calculation of ROIs, the details were as follows: (1) The slice was chosen around the uppermost layer of the lateral ventricle body by limiting the Z value; (2) The ROIs of the association and projection fibers were chosen on the above plane by selecting X and Y and ensuring that the Y values were consistent (i.e., the two ROIs were in the same horizontal direction) with the direction of the deep veins; (3) All optional ROI positions satisfying the above conditions (XYZ) were traversed to maximize the values inside the association and projection ROI to eliminate the influence of other oriented bundles as much as possible. Subsequently, the values of Dxx, Dyy, and Dzz inside the ROIs of the association and projection fibers were extracted from the images obtained in the previous preprocessing steps, and the ALPS indices were calculated according to the following formula: 

ALPS index=  (mean (Dxxproj,Dxxassoci))/(mean (Dyyproj,Dzzassoci) )

All steps were calculated separately for the left and right hemispheres to obtain ALPS indices for the left and right brain, respectively, and the mean values were used for statistical analysis.

The process from the preprocessing of the original DTI data to the final generation of ALPS values was fully automated, without the need for manual correction. An image of the ROI superimposed on the FA color map was generated for rapid quality control.

## Requirements
For DTI preprocessing in Shell
* MRtrix3
* FSL
* AFNI
* CUDA

For Auto ALPS Calculation and QC in Python
* nibabel
* numpy
* PIL
* csv

## How to use
DTI preprocessing for each subject (about 10-30 minutes for single subject, parallel run is reconmmeded)
```sh
./1_DTI_preprocessing.sh
```

Auto ALPS Calculation and QC for all subjects  (less than 5 seconds for single subject)
```sh
python3 ./2_Automated_DTI-ALPS.py
```
## Results
All subjects' bilateral ALPS values would be recorded in the results.csv

All subjects' bilateral QC images would be saved in the subject_l/r.jpg

## References
* Tatekawa H, Matsushita S, Ueda D, et al. Improved reproducibility of diffusion tensor image analysis along the perivascular space (DTI-ALPS) index: an analysis of reorientation technique of the OASIS-3 dataset. Japanese Journal of Radiology. 2023;41(4):393-400.

* Zhang W, Zhou Y, Wang J, et al. Glymphatic clearance function in patients with cerebral small vessel disease. Neuroimage. 2021;238:118257.
