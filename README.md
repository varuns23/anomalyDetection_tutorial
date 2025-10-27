# CMS Open Data Anomaly Detection Exercises

These exercises are to be used for HSF-India Hackathon to be held at University of Hyderabad and have been adopted from AD4HEP workshop, June 2025, Nevis Labs, Columbia University 

These exercises are designed to be as light on requirements as possible. In general, if you have a linux system with python on it, and a way to look at a Jupyter notebook, you should be able to run these exercises.

You will be using the University of Wisconsin Analysis Facility (https://cms01.hep.wisc.edu)

We  have provided a quick setup script, `setup.sh`.
It will make a python virtual environment, and install several necessary packages. Do not run it more than once.
If you haven't used a virtual environment before, it can be activated (in bash) with `source ad_tutorial_env/bin/activate` and deactivated via `deactivate`.
Any packages installed in a virtual environment will only affect that virtual environment.
The script should leave you in it by default, but if you need to get back in, just activate it again.

The exercises are in jupyter notebooks. If you are `ssh`'d into a machine, we recommend you use port forwarding via:
```
ssh -L <random 4 digit number>:localhost:<the same random 4 digit number> <you>@<hosting machine>
```

And starting the jupyter notebook like so:
```
jupyter notebook --no-browser --port <the same random 4 digit number as before>
```

Jupyter should provide you a local host link you can go to. Open that on your machine, the port forwarding should allow you to access the notebook on the remote machine.

### Data File Creation
We have included several basic converter scripts here designed to be used alongside Snakemake. If for any reason, you need to recreate the files in `data/`, you will need to be on an XRootD capable machine/account. The files can be created via a simple snakemake command (but may take some time). The ROOT files can be removed later.

### Note:

We should very much cite _Hands-On Machine Learning with Scikit-Learn and TensorFlow_ by by Aurélien Géron (2017,  O'Reilly Media, Inc. ISBN: 9781491962299) which is an excellent resource for machine learning and neural networks (especially for beginners) ([link here](https://www.oreilly.com/library/view/hands-on-machine-learning/9781491962282/)), and was crucial in making the GAN Anomaly Detection loop, which we always need to look up again. Please see the repository for the book's code [here](https://github.com/ageron/handson-ml2/tree/master). Note that all work in that repository is under an [Apache 2 license](https://www.apache.org/licenses/LICENSE-2.0).

If you are a beginner with machine learning, the exercises here make use of [SciKit-Learn](https://scikit-learn.org/stable/) (Scikit-learn: Machine Learning in Python, Pedregosa et al., JMLR 12, pp. 2825-2830, 2011), and [Tensorflow/Keras](https://keras.io/). We highly recommend familiarizing yourself with the libraries and APIs they provide. SciKit-Learn is under a [BSD 3-Clause License](https://opensource.org/license/bsd-3-clause), and keras is under an [Apache 2 license](https://www.apache.org/licenses/LICENSE-2.0).

The data files for this exercise will take up about 5 Gb. The environment will take approximately 3 Gb.

All exercises here are done with 2016 CMS open data. [See the CERN open data portal for more information](https://opendata.cern.ch/)

In particular, We use:
- `/eos/opendata/cms/derived-data/PFNano/29-Feb-24/ZeroBias/Run2016G-UL2016_MiniAODv2_PFNanoAODv1/`
- `/eos/opendata/cms/derived-data/PFNano/29-Feb-24/JetHT/Run2016G-UL2016_MiniAODv2_PFNanoAODv1/`
- `/eos/opendata/cms/mc/RunIISummer20UL16NanoAODv9/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/`
- `/eospublic.cern.ch//eos/opendata/cms/mc/RunIISummer20UL16NanoAODv9/GluGluToRadionToHHTo2B2ZTo2L2J_M-500_narrow_TuneCP5_PSWeights_13TeV-madgraph-pythia8/NANOAODSIM/`
- `/eos/opendata/cms/mc/RunIISummer20UL16NanoAODv9/QCD_Pt-5to10_TuneCP5_Flat2018_13TeV_pythia8/NANOAODSIM/`
