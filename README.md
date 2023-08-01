# Multisensory-B-module
Code for B module with Christian and Felix to analyze optic lobe signals from two-photon imaging experiments.


## Package for motion correction
We are using CaImAn. To download and set up:

Follow instructions on but use conda instead of mamba [CaImAn](https://caiman.readthedocs.io/en/master/Installation.html#installing-caiman). Some notes (read before installing!):
- Use the "environment-minimal.yml" file but edit it so it uses python 3.9 (higher python versions have a deprecation in an in-built package of python which conflicts with CaImAn)
- Install also the pims package.

