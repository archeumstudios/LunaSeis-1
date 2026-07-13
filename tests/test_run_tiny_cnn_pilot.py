import unittest

import numpy as np
import torch

from scripts.run_tiny_cnn_pilot import TinyCNN, average_precision, bin_valid_means, deterministic_negative_rows, fixed_length


class TinyCNNPilotTests(unittest.TestCase):
    def test_model_shape_and_size(self):
        model=TinyCNN()
        self.assertEqual(tuple(model(torch.zeros(3,2,4096)).shape),(3,))
        self.assertLess(sum(value.numel() for value in model.parameters()),10_000)

    def test_gap_aware_binning(self):
        values=np.array([1.,-1.,3.,5.]);missing=np.array([False,True,False,False])
        signal,coverage=bin_valid_means(values,missing,bins=2)
        np.testing.assert_allclose(signal,[1.,4.]);np.testing.assert_allclose(coverage,[.5,1.])

    def test_native_fixed_length_preserves_samples_and_mask(self):
        signal,coverage=fixed_length(np.array([2.,-1.,4.]),np.array([False,True,False]),length=5)
        np.testing.assert_allclose(signal,[2.,0.,4.,0.,0.]);np.testing.assert_allclose(coverage,[1.,0.,1.,0.,0.])

    def test_negative_choice_is_deterministic(self):
        rows=[{"station":"S12","channel":"MHZ","start_time":str(i)} for i in range(8)]
        self.assertEqual(deterministic_negative_rows(rows,3),deterministic_negative_rows(rows,3))

    def test_average_precision(self):
        self.assertEqual(average_precision(np.array([.9,.8,.1]),np.array([1,1,0])),1.0)
