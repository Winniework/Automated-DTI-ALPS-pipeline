#!/bin/bash

## to create reoriented images dti.nii.gz, dti.bvec, dti.bval, and ICBM_FA.nii.gz (FA template) should be prepared
## this technique used MRtrix3, FSL, and AFNI software

## convert nifti to mif
mrconvert dti.nii.gz dti.mif -fslgrad dti.bvec dti.bval -datatype float32  # MRtrix3

## denoise
dwidenoise dti.mif dti_den.mif -noise dti_noise.mif  # MRtrix3

## remove gibbs artifact
mrdegibbs dti_den.mif dti_den_unr.mif -axes 0,1  # MRtrix3

## eddy and motion correct (if needed, correct for TopUp)
dwifslpreproc dti_den_unr.mif dti_den_unr_preproc.mif -pe_dir AP -rpe_none -eddy_options " --slm=linear"  # MRtrix3

## b1field correction
dwibiascorrect ants dti_den_unr_preproc.mif dti_den_unr_preproc_unbiased.mif -bias bias.mif  # MRtrix3
# dwibiascorrect -ants dti_den_unr_preproc.mif dti_den_unr_preproc_unbiased.mif -bias bias.mif  # for some environment this code may work

## create brain_mask of dwi
dwi2mask dti_den_unr_preproc_unbiased.mif mask_den_unr_preproc_unbiased.nii.gz  # MRtrix3

## Convert to nifti
mrconvert dti_den_unr_preproc_unbiased.mif dti_den_unr_preproc_unbiased.nii.gz -export_grad_fsl dti_den_unr_preproc_unbiased.bvec dti_den_unr_preproc_unbiased.bval  # MRtrix3

## when brain mask or b0 brain are needed, please use below
# 3dTcat dti_den_unr_preproc_unbiased.nii.gz[0] -prefix b0.nii.gz  # AFNI
# cp mask_den_unr_preproc_unbiased.nii.gz b0_brain_mask.nii.gz
# 3dcalc -a b0.nii.gz -b b0_brain_mask.nii.gz -expr "a*b" -prefix b0_brain.nii.gz  # AFNI

## create FA, MD, V1, tensor, etc
dtifit --bvals=dti_den_unr_preproc_unbiased.bval --bvecs=dti_den_unr_preproc_unbiased.bvec --data=dti_den_unr_preproc_unbiased.nii.gz --mask=mask_den_unr_preproc_unbiased.nii.gz --out=dti --save_tensor  # FSL

## dti.tensor.nii.gz, dti_FA.nii.gz, dti_V1.nii.gz, and ICBM_FA.nii.gz (FA template) are needed for the following procedure
## create diffusivity of Dxx, Dyy, Dzz
3dTcat dti_tensor.nii.gz[0] -prefix dti_Dxx.nii.gz  # AFNI
3dTcat dti_tensor.nii.gz[3] -prefix dti_Dyy.nii.gz  # AFNI
3dTcat dti_tensor.nii.gz[5] -prefix dti_Dzz.nii.gz  # AFNI

## create color map
3dcalc -prefix DTIout.nii.gz -a 'dti_V1.nii.gz[0..2]' -c 'dti_FA.nii.gz' -expr 'c*step(c-0.25)*255*abs(a)'  # AFNI
3dThreetoRGB -prefix DTI_ColorMap.nii.gz -anat DTIout.nii.gz  # AFNI

## flirt to ICBM_FA.nii.gz (FA template)
flirt -ref ICBM_FA.nii.gz -in dti_FA.nii.gz -omat fa2mni.mat -dof 6  # FSL
flirt -in dti_FA.nii.gz -ref ICBM_FA.nii.gz -applyxfm -init fa2mni.mat -o dti_FA_reoriented.nii.gz  # FSL

## vecreg function is used
vecreg -i dti_tensor.nii.gz -o dti_reoriented_tensor.nii.gz -r ICBM_FA.nii.gz -t fa2mni.mat  #FSL
vecreg -i dti_V1.nii.gz -o dti_reoriented_V1.nii.gz -r ICBM_FA.nii.gz -t fa2mni.mat  #FSL

## create reoriented diffusivity of Dxx, Dyy, Dzz
3dTcat dti_reoriented_tensor.nii.gz[0] -prefix dti_reoriented_Dxx.nii.gz  # AFNI
3dTcat dti_reoriented_tensor.nii.gz[3] -prefix dti_reoriented_Dyy.nii.gz  # AFNI
3dTcat dti_reoriented_tensor.nii.gz[5] -prefix dti_reoriented_Dzz.nii.gz  # AFNI

## create reoriented color map
3dcalc -prefix DTIout_reoriented.nii.gz -a 'dti_reoriented_V1.nii.gz[0..2]' -c 'dti_FA_reoriented.nii.gz' -expr 'c*step(c-0.25)*255*abs(a)'  # AFNI
3dThreetoRGB -prefix DTI_reoriented_ColorMap.nii.gz -anat DTIout_reoriented.nii.gz  # AFNI
