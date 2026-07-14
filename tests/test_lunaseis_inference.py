import unittest

import numpy as np
import torch

from lunaseis.model import DepthwiseCNN,preprocess


class LunaSeisInferenceTests(unittest.TestCase):
    def test_model_shape_and_parameter_budget(self):
        model=DepthwiseCNN();self.assertEqual(model(torch.zeros(2,2,4096)).shape,(2,));self.assertLess(sum(p.numel() for p in model.parameters()),10000)
    def test_preprocessing_is_bounded_and_gap_aware(self):
        sample=preprocess(np.array([10.,11.,-1.,1e6,12.]),length=8);self.assertEqual(sample.shape,(2,8));self.assertEqual(sample[1,2],0);self.assertLessEqual(np.max(np.abs(sample[0])),20)
    def test_excessive_gap_rejected(self):
        self.assertIsNone(preprocess(np.array([-1.,-1.,1.,2.])))


if __name__=="__main__":unittest.main()
