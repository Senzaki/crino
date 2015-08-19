# Crino: a neural-network library based on Theano

Crino is an open-source Python library aimed at building and training artificial neural-networks. It has been developed on top of [Theano](http://deeplearning.net/software/theano/), by researchers from the [LITIS laboratory](http://www.litislab.eu). It helps scientists and/or programmers to design neural-network architectures adapted to their needs, using a modular framework inspired by [Torch](http://torch5.sourceforge.net/manual/nn/). Our library also provides vanilla implementations, and learning algorithms, for these architectures :
* auto-encoders (AE)
* multi-layer perceptrons (MLP)
* deep neural networks (DNN)
* input-output deep architectures (IODA)
 
IODA is a novel DNN architecture, which is useful in cases where both input and output spaces are high-dimensional, and where there are strong interdependences between output labels. The input and output layers of a IODA are initialized with an unsupervised pre-training step, based on the stacked auto-encoder strategy, commonly used in DNN training algorithms. Then, the backpropagation algorithm performs the final supervised learning step.

Crino and IODA are research topics of the [Deep in Normandy](http://deep.normastic.fr/) research program of the  [NormaSTIC](http://www.normastic.fr/) federation, which has been awarded as a [NVIDIA GPU Research Center](https://developer.nvidia.com/academia/centers/normastic) in 2015.

## Getting started
* Install Crino :
```bash
cd to/some/path
git clone https://github.com/jlerouge/crino.git
cd crino
sudo python setup.py install
```

* Run the given example :
```bash
cd example
chmod +x example.py
./example.py
```
* Adapt it to your needs! Crino is natively compatible with Matlab-like data or any format handled by SciPy/NumPy.
* Check the project [documentation](http://jlerouge.github.io/crino/doc).

## FAQ
* **What does "device gpu is not available" mean ?**
    Your GPU card may not be compatible with CUDA technology (check http://www.geforce.com/hardware/technology/cuda/supported-gpus). If so, there is nothing to do. Otherwise, your theano installation may have a  problem (see http://deeplearning.net/software/theano/install.html#using-the-gpu).
* **Where does the name "Crino" come from ?**
    We developed this library as an extension of Theano. In Greek mythology, Crino is the daughter of Theano.

## About our project
### Citing Crino/IODA
If you use Crino and/or our IODA framework for academic research, you are highly encouraged (though not required) to cite the following paper:
* J. Lerouge, R. Herault, C. Chatelain, F. Jardin and R. Modzelewski, ["IODA: an Input/Output Deep Architecture for image labeling"](http://www.sciencedirect.com/science/article/pii/S0031320315001181), Pattern Recognition (2015), DOI: 10.1016/j.patcog.2015.03.017 [Epub ahead of print]

### Credits
We would like to thank the authors of [Theano](http://deeplearning.net/software/theano/) :
* J. Bergstra, O. Breuleux, F. Bastien, P. Lamblin, R. Pascanu, G. Desjardins, J. Turian, D. Warde-Farley and Y. Bengio. [“Theano: A CPU and GPU Math Expression Compiler”](http://www.iro.umontreal.ca/~lisa/pointeurs/theano_scipy2010.pdf). Proceedings of the Python for Scientific Computing Conference (SciPy) 2010. June 30 - July 3, Austin, TX

IODA is partly based on the original work of B. Labbé et al. :
* B. Labbé, R. Hérault and C. Chatelain . [“Learning Deep Neural Networks for High Dimensional Output Problems”](http://hal.archives-ouvertes.fr/docs/00/43/87/14/PDF/icmla09.pdf). In IEEE International Conference on Machine Learning and Applications (ICMLA'09), December 2009.

### Contact
You can contact us with the following e-mail address : crino-contact@litislab.fr.
Feel free to open a new [issue](https://github.com/jlerouge/crino/issues) in case you have found a bug in Crino.
