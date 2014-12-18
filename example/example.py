#!/usr/bin/env python
# -*- coding: utf-8 -*-

#    Copyright (c) 2014 Clément Chatelain, Romain Hérault, Julien Lerouge,
#    Romain Modzelewski (LITIS - EA 4108). All rights reserved.
#    
#    This file is part of Crino.
#
#    Crino is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Crino is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with Crino. If not, see <http://www.gnu.org/licenses/>.

import os,os.path
import sys

import numpy as np

import scipy
import scipy.io as sio

import theano
import theano.tensor as T

import crino
from crino.network import PretrainedMLP
from crino.criterion import MeanSquareError

import cPickle as pickle
import json
import csv


def defaultConfig():

    config={}
    
    #Learning parameters of the input pretraining
    input_pretraining_params={
            'learning_rate': 1.0,
            'batch_size' : 100,
            'epochs' : 300
            }
    
    #Learning parameters of the output pretraining
    output_pretraining_params={
            'learning_rate': 1.0,
            'batch_size' : 100,
            'epochs' : 300
            }
    
    #Learning parameters of the link pretraining
    link_pretraining_params={
            'learning_rate': 1.0,
            'batch_size' : 100,
            'epochs' : 300
            }
    
    #Learning parameters of the supervised training + pretrainings
    config['learning_params']={
        'learning_rate' : 1.0,
        'batch_size' : 100,
        'epochs' : 300,
        'input_pretraining_params' : input_pretraining_params,
        'output_pretraining_params' : output_pretraining_params,
        'link_pretraining_params' : link_pretraining_params,
        'link_pretraining' : True
    }
    
    #Size of one hidden representation
    hidden_size = 1024
    #Geometry of all hidden representations 
    config['hidden_geometry'] = [hidden_size,hidden_size]

    #How many layers are pretrained (here 1 at input and 1 at output) 
    config['pretraining_geometry']={
        'nInputLayers': 1,
        'nOutputLayers': 1
    }

    #Shall we used known init weights
    config['init_weights'] = None
    #Shall we save init weights
    config['save_init_weights'] = True
    
    #Examples to be displayed at testing
    config['displayed_examples']=[10,50,100]

    #Epochs to be displayed at testing
    config['displayed_epochs']=[0,10,100,200,300]

    #Where to store results
    config['outfolder']='./default_config_example_results/'
    
    return config


class MyPretrainedMLP(PretrainedMLP):
    
    def setDisplayedEpochs(self,displayed_epochs):
        self.displayed_epochs=displayed_epochs        
    
    def setTestSet(self,x_test,y_test):
        self.shared_x_test=theano.shared(x_test)
        self.shared_y_test=theano.shared(y_test)
        
    def initEpochHook(self):
        self.testCriterionFunction=self.criterionFunction(downcast=True, shared_x_data=self.shared_x_test, shared_y_data=self.shared_y_test)
        self.testForwardFunction=self.forwardFunction(downcast=True, shared_x_data=self.shared_x_test)
        
        self.test_criterion_history=[np.mean(self.testCriterionFunction())]
        self.test_forward_history=[(-1,self.testForwardFunction())]
        
        self.appForwardFunction=self.forwardFunction(downcast=True, shared_x_data=self.finetunevars['shared_x_train'])
        self.app_forward_history=[(-1,self.appForwardFunction())]
        
    def checkEpochHook(self):
        self.test_criterion_history.append(np.mean(self.testCriterionFunction()))
        if self.finetunevars['epoch']+1 in self.displayed_epochs:
            self.test_forward_history.append((self.finetunevars['epoch'],self.testForwardFunction()))
            self.app_forward_history.append((self.finetunevars['epoch'],self.appForwardFunction()))


def data2greyimg(filename, X):
    Xn=(X-X.min())/(X.max()-X.min())*255
    scipy.misc.imsave(filename, Xn)
    

def experience(config):
    
    needed_params=['learning_params','hidden_geometry','pretraining_geometry','init_weights','save_init_weights','displayed_examples','displayed_epochs','outfolder']

    used_config={}
    for aParam in needed_params:
        if not( aParam in config.keys()):
            raise ValueError("Experience configuration does not contain %s parameter"%(aParam))
        exec '%s=pickle.loads("""%s""")'%(aParam,pickle.dumps(config[aParam]))
        used_config[aParam]=config[aParam]

    absoutfolder=os.path.abspath(outfolder)
    if not os.path.exists(absoutfolder):
        os.mkdir(absoutfolder)
    
    print('... saving used configuration')
    json.dump(used_config,open(os.path.join(absoutfolder,"configuration.json"),'wb'),indent=2)
    
    print '... loading training data'
    train_set = sio.loadmat('data/fixed/train.mat')
    x_train = np.asarray(train_set['x_train'], dtype=theano.config.floatX) # We convert to float32 to 
    y_train = np.asarray(train_set['y_train'], dtype=theano.config.floatX) # compute on GPUs with CUDA

    print '... loading test data'
    test_set = sio.loadmat('data/fixed/test.mat')
    x_test = np.asarray(test_set['x_test'], dtype=theano.config.floatX) # We convert to float32 to
    y_test = np.asarray(test_set['y_test'], dtype=theano.config.floatX) # compute on GPUs with CUDA


    nApp = x_train.shape[0] # number of training examples
    nTest = x_test.shape[0] # number of training examples
    nFeats = x_train.shape[1] # number of pixels per image
    xSize = int(np.sqrt(nFeats)) # with of a square image

    # Input representation size is the number of pixel
    nInputs=nFeats
    # Output representation size is the number of pixel
    nOutputs=nFeats
    
    # Compute the full geometry of the MLP
    geometry=[nFeats] + hidden_geometry+[nFeats]
    # Compute the number of layers
    nLayers=len(geometry)-1

    results={}
  
    for phase,xdata,ydata in [['train',x_train,y_train],['test',x_test,y_test]]:  
        for ex in displayed_examples:
            x_orig = np.reshape(xdata[ex:ex+1], (xSize, xSize), 'F')
            data2greyimg(os.path.join(absoutfolder,"%s_ex_%03d_input.png"%(phase,ex,)),x_orig)
            y_true = np.reshape(ydata[ex:ex+1], (xSize, xSize), 'F')
            data2greyimg(os.path.join(absoutfolder,"%s_ex_%03d_target.png"%(phase,ex,)),y_true)


    print '... building and learning a network'
    nn = MyPretrainedMLP(geometry, outputActivation=crino.module.Sigmoid,**pretraining_geometry)
    
    nn.setTestSet(x_test,y_test)
    nn.setDisplayedEpochs(displayed_epochs)
    
    nn.linkInputs(T.matrix('x'), nFeats)
    nn.prepare()
    nn.criterion = MeanSquareError(nn.outputs, T.matrix('y'))
    if not(init_weights is None):
        nn.setParameters(init_weights)
    if save_init_weights:
        pickle.dump(init_weights,open(os.path.join(absoutfolder,"starting_params.pck"),'w'),protocol=-1)

    delta = nn.train(x_train, y_train, **learning_params)
    print '... learning lasted %s (s) ' % (delta)
    
    results={
        'I':pretraining_geometry['nInputLayers'],
        'L':nLayers-pretraining_geometry['nInputLayers']-pretraining_geometry['nOutputLayers'],
        'O':pretraining_geometry['nOutputLayers'],
        'train_criterion':nn.finetunevars['history'][-1],
        'train_history':nn.finetunevars['history'],
        'train_full_history':nn.finetunevars['full_history'],
        'test_criterion': nn.test_criterion_history[-1],
        'test_history':nn.test_criterion_history,
        }
    pickle.dump(nn.getParameters(),open(os.path.join(absoutfolder,"learned_params.pck"),'w'),protocol=-1)
    
    for phase,xdata,ydata,history in [
                ['train',x_train,y_train,nn.app_forward_history],
                ['test',x_test,y_test,nn.test_forward_history]]:
        for ex in displayed_examples:
            for epoch,forward in history:
                y_estim = np.reshape(forward[ex:ex+1], (xSize, xSize), 'F')
                data2greyimg(os.path.join(absoutfolder,"%s_ex_%03d_estim_%03d.png"%(phase,ex,epoch+1)),y_estim)
                    
    pickle.dump(results,open(os.path.join(absoutfolder,'results.pck'),'w'),protocol=-1)  
    
    table=[["Input Pretrained Layers","Link Layers","Output Pretrained Layers", "Epoch","Train", "Test"]]
    for epoch in displayed_epochs:
        table.append([results['I'],results['L'],results['O'],epoch,results['train_history'][epoch],results['test_history'][epoch]])

    writer=csv.writer(open(os.path.join(absoutfolder,'results.csv'),'wb'),delimiter='\t')
    for row in table:
        writer.writerow(row)

def main():
    experience(defaultConfig())

if __name__=="__main__":
    main()
