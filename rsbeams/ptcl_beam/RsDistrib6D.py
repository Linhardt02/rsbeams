# -*- coding: utf-8 -*-
"""Generate a Gaussian or uniformly-filled 6D distribution.

Original code taken from RadTrack project, https://github.com/radiasoft/radtrack
:copyright: Copyright (c) 2013 RadiaBeam Technologies, LLC. All Rights Reserved.

Subsequent mods are due to RadiaSoft,
:copyright: Copyright (c) 2017 Radiasoft LLC. All Rights Reserved.

:license: http://www.apache.org/licenses/LICENSE-2.0.html
"""
import math
import numpy
from rsbeams.ptcl_beam import RsTwiss2D
from rsbeams.ptcl_beam import RsPhaseSpace6D
from rsbeams.statistics import stats6d

class RsDistrib6D:
"""Generate a Gaussian or uniformly-filled 6D distribution."""

    def __init__(self, num_ptcls):
        # for testing purposes only
        if False:
            print ' '
            print ' ...in RsDistrib6D:__init__'
            print ' phase_space_6d object will be instantiated!'

        self.phase_space_6d = RsPhaseSpace6D.RsPhaseSpace6D(num_ptcls)
        self.phase_space_6d.checkArray()

        # set some defaults
        self.maxRmsFactor = 5.0
        self.distrib_type = 'gaussian'
        return

    def get_phase_space_6d(self):
        return self.phase_space_6d

    def get_distrib_type(self):
        return self.distrib_type

    def set_distrib_type(self, distrib_type):
        if ( (distrib_type == 'uniform')  or
             (distrib_type == 'gaussian') or
             (distrib_type == 'waterbag') or
             (distrib_type == 'kv') ):
            self.distrib_type = distrib_type
        else:
            message = 'distrib_type = ' + self.distrib_type + ' -- not supported.'
            raise Exception(message)
        return

    def get_max_rms_fac(self):
        return self.max_rms_fac

    def set_max_rms_fac(self, max_rms_fac):
        # error handling of input data
        if (max_rms_fac > 0.0):
            self.max_rms_fac = max_rms_fac
        else:
            message = 'max_rms_fac = ' + str(max_rms_fac) + '; must be > 0.'
            raise Exception(message)
        return

    def make_unif_distrib(self):
        array6D = self.phase_space_6d.getArray6D()
        num_ptcls = self.phase_space_6d.getNumParticles()
        num_inside_circle = 0
        while (num_inside_circle < num_ptcls):
            testX = 2. * numpy.random.uniform(0.0,1.0,1) - 1.
            testY = 2. * numpy.random.uniform(0.0,1.0,1) - 1.
            testZ = 2. * numpy.random.uniform(0.0,1.0,1) - 1.
            testSum = testX**2 + testY**2 + testZ**2

            if (testSum < 1.):
                array6D[0, num_inside_circle] = testX
                array6D[2, num_inside_circle] = testY
                array6D[4, num_inside_circle] = testZ
                num_inside_circle += 1

        num_inside_circle = 0
        while (num_inside_circle < num_ptcls):
            testPx = 2. * numpy.random.uniform(0.0,1.0,1) - 1.
            testPy = 2. * numpy.random.uniform(0.0,1.0,1) - 1.
            testPz = 2. * numpy.random.uniform(0.0,1.0,1) - 1.
            testSum = testPx**2 + testPy**2 + testPz**2

            if (testSum < 1.):
                array6D[1, num_inside_circle] = testPx
                array6D[3, num_inside_circle] = testPy
                array6D[5, num_inside_circle] = testPz
                num_inside_circle += 1

        return

    def make_gauss_distrib(self):
        array6D = self.phase_space_6d.getArray6D()
        num_ptcls = self.phase_space_6d.getNumParticles()
        for nLoop in range(6):
            num_inside_circle = 0
            while (num_inside_circle < num_ptcls):
                testPoint = numpy.random.normal(0.0, 1.0, 1)

                if (testPoint*testPoint < self.max_rms_fac):
                    array6D[nLoop, num_inside_circle] = testPoint
                    num_inside_circle += 1
        return

    def init_phase_space_6d(self):
        if (self.distrib_type == 'uniform'):
            self.make_unif_distrib()
        elif (self.distrib_type == 'gaussian'):
            self.make_gauss_distrib()
        elif (self.distrib_type == 'waterbag'):
            message = 'distrib_type = ''waterbag'' is not yet implemented.'
            raise Exception(message)
        elif (self.distrib_type == 'kv'):
            message = 'distrib_type = ''kv'' is not yet implemented.'
            raise Exception(message)
        else:
            message = 'distrib_type = ' + self.distrib_type + ' -- not supported.'
            raise Exception(message)
        return

    def clean_phase_space_6d(self):
        stats6d.sub_avg6d(self.phase_space_6d.getArray6D())
        stats6d.rm_correlations6d(self.phase_space_6d.getArray6D())
        stats6d.sub_avg6d(self.phase_space_6d.getArray6D())
        stats6d.normalize_rms6d(self.phase_space_6d.getArray6D())
        return

    def round_phase_space_6d(self):
        self.init_phase_space_6d()
        self.clean_phase_space_6d()
        return

    def calc_averages_6d(self):
        averages = stats6d.calc_avg6d(self.phase_space_6d.getArray6D())
        return averages

    def calc_rms_values_6d(self):
        rmsValues = stats6d.calcRmsValues6D(self.phase_space_6d.getArray6D())
        return rmsValues

    def calc_twiss_params_6d(self,twiss_params_6d):
        alphaRMS = numpy.zeros(3)
        betaRMS  = numpy.zeros(3)
        emitRMS  = numpy.zeros(3)

        sigma = stats6d.calcCorrelations6D(self.phase_space_6d.getArray6D())
        for iLoop in range(3):
            ii = 2 * iLoop
            emitSQ = sigma[ii,ii]*sigma[ii+1,ii+1] - sigma[ii,ii+1]*sigma[ii+1,ii]

            if False:
                print ' '
                print ' num_ptcls = ', self.phase_space_6d.getNumParticles()
                q6 = self.phase_space_6d.getArray6D()
                print ' 1st particle: ', q6[:,0]

            if False:
                print ' '
                print ' iLoop, ii = ', iLoop, ii
                print ' sigma[', ii,   ii,  '] = ', sigma[ii,  ii  ]
                print ' sigma[', ii+1, ii,  '] = ', sigma[ii+1,ii  ]
                print ' sigma[', ii,   ii+1,'] = ', sigma[ii,  ii+1]
                print ' sigma[', ii+1, ii+1,'] = ', sigma[ii+1,ii+1]

            if emitSQ <= 0.0:
                message  = 'Error -- \n\n'
                message += '  emitSQ = ' + str(emitSQ) + ' must be > zero!\n'
                message += '  ...in RsDistrib6D:calc_twiss_params_6d()\n'
                message += '  iLoop, ii = ' + str(iLoop) + ', ' + str(ii) + '\n'
                raise Exception(message)

            emitRMS[iLoop]  =  math.sqrt(emitSQ)
            betaRMS[iLoop]  =  sigma[ii,ii]   / emitRMS[iLoop]
            alphaRMS[iLoop] = -sigma[ii,ii+1] / emitRMS[iLoop]

            if False:
                print ' '
                print ' alphaRMS, betaRMS, emitRMS = ', alphaRMS[iLoop], betaRMS[iLoop], emitRMS[iLoop]

        twiss_params_6d['twissX'] = RsTwiss2D.RsTwiss2D(alphaRMS[0], betaRMS[0], emitRMS[0])
        twiss_params_6d['twissY'] = RsTwiss2D.RsTwiss2D(alphaRMS[1], betaRMS[1], emitRMS[1])
        twiss_params_6d['twissZ'] = RsTwiss2D.RsTwiss2D(alphaRMS[2], betaRMS[2], emitRMS[2])
        return

    def makeTwissDist6D(self,twiss_params_6d, meanMomentum):
        self.round_phase_space_6d()

        array6D = self.phase_space_6d.getArray6D()
        temp6D = array6D.copy()

        ii = -1
        for iLoop in range(0,5,2):

            ii +=1
            if   ii==0: twissObject = twiss_params_6d['twissX']
            elif ii==1: twissObject = twiss_params_6d['twissY']
            elif ii==2: twissObject = twiss_params_6d['twissZ']
            else:
                message = 'Error:  ii = ' + ii + ' -- not valid.'
                raise Exception(message)

            alphaII = twissObject.getAlphaRMS()
            betaII  = twissObject.getBetaRMS()
            gammaII = (1.0 + alphaII**2) / betaII

            if 0:
                print ' '
                print ' alpha, beta, gamma[', ii, '] = ', alphaII, betaII, gammaII

            gMinusB = gammaII - betaII
            rootFac = math.sqrt(gMinusB**2 + 4.0*alphaII**2)

            if 0:
                print ' gMinusB, rootFac[', ii, '] = ', gMinusB, rootFac

            if gMinusB >= 0.0:
                fac  = math.sqrt(0.5*(gammaII+betaII-rootFac))
                fInv = math.sqrt(0.5*(gammaII+betaII+rootFac))
            else:
                fac  = math.sqrt(0.5*(gammaII+betaII+rootFac))
                fInv = math.sqrt(0.5*(gammaII+betaII-rootFac))

            if 0:
                print ' fac, fInv[', ii, '] = ', fac, fInv

            if alphaII == 0.0:
                sinPhi = 0.0
                cosPhi = 1.0
            else:
                sinPhi = math.sqrt(0.5*(1.-math.fabs(gMinusB)/rootFac))
                cosPhi = math.sqrt(0.5*(1.+math.fabs(gMinusB)/rootFac))

            if alphaII*gMinusB < 0.0: sinPhi = -sinPhi

            rootFac = math.sqrt(twissObject.getEmitRMS())

            if 0:
                print ' sinPhi, cosPhi, rootFac[', ii, '] = ', sinPhi, cosPhi, rootFac

            for nLoop in range(self.phase_space_6d.getNumParticles()):
                array6D[iLoop  ,nLoop] = rootFac*(fac *cosPhi*temp6D[iLoop,  nLoop] - \
                                                  fInv*sinPhi*temp6D[iLoop+1,nLoop])
                array6D[iLoop+1,nLoop] = rootFac*(fac *sinPhi*temp6D[iLoop,  nLoop] + \
                                                  fInv*cosPhi*temp6D[iLoop+1,nLoop])
        self.multiplyDistribComp(meanMomentum, 5)
        self.offsetDistribComp(meanMomentum, 5)

    def offsetDistribComp(self,offset,index):
        if index < 0 or index > 5:
            message = 'ERROR!  index is out of range: ' + str(index)
            raise Exception(message)

        array6D = self.phase_space_6d.getArray6D()
        array6D[index,:] += offset

        return

    def multiplyDistribComp(self,factor,index):
        if index < 0 or index > 5:
            message = 'ERROR!  index is out of range: ' + str(index)
            raise Exception(message)

        array6D = self.phase_space_6d.getArray6D()
        array6D[index,:] *= factor

        return