import os
import zipfile
import numpy as np
import torch
from torch_geometric.utils import dense_to_sparse
from six.moves import urllib
from torch_geometric_temporal.data.discrete.static_graph_discrete_signal import StaticGraphDiscreteSignal


class METRLADatasetLoader(object):
    """A traffic forecasting dataset based on Los Angeles
    Metropolitan traffic conditions. The dataset contains traffic
    readings collected from 207 loop detectors on highways in Los Angeles 
    County in aggregated 5 minute intervals for 4 months between March 2012 
    to June 2012.
    """

    def __init__(self, arg):
        super(MetrlaDatasetLoader, self).__init__()

    def _read_web_data(self):
        url = "placeholder"

        # Check if zip file is in data folder from working directory, otherwise download
        if (not os.path.isfile("data/METR-LA.zip")):
            urllib.request.urlopen(url).read()

        if (not os.path.isfile("data/adj_mat.npy") or not os.path.isfile("data/node_values.npy")):
            with zipfile.Zipfile("data/METR-LA.zip", "r") as zip_fh:
                zip_fh.extractall("data/")

        A = np.load("data/adj_mat.npy")
        X = np.load("data/node_values.npy").transpose((1,2,0))
        X = X.astype(np.float32)

        # Normalise as in DCRNN paper (via Z-Score Method)
        means = np.mean(X, axis=(0, 2))
        X = X - means.reshape(1, -1, 1)
        stds = np.std(X, axis=(0, 2))
        X = X / stds.reshape(1, -1, 1)
        
        self.A = torch.from_numpy(A)
        self.X = torch.from_numpy(X)

    def _get_edges(self):
        edge_indices, values = dense_to_sparse(self.A)
        edge_indices = edge_indices.numpy()
        self.edges = edge_indices

    def _get_edge_weights(self):
        self.edge_weights = np.ones(self.edges.shape[1])

    def _generate_task(self, num_timesteps_in: int=12, num_timesteps_out: int=12):
        """Uses the node features of the graph and generates a feature/target
        relationship of the shape
        (num_nodes, num_node_features, num_timesteps_in) -> (num_nodes, num_timesteps_out)
        predicting the average traffic speed using num_timesteps_in to predict the
        traffic conditions in the next num_timesteps_out

        Args:
            num_timesteps_in (int): number of timesteps the sequence model sees
            num_timesteps_out (int): number of timesteps the sequence model has to predict
        """
        pass

    def get_dataset(self, num_timesteps_in: int=12, num_timesteps_out: int=12) -> StaticGraphDiscreteSignal:
        """Returns data iterator for METR-LA dataset as an instance of the
        static graph discrete signal class.

        Return types:
            * **dataset** *(StaticGraphDiscrete Signal)* - The METR-LA traffic
                forecasting dataset.
        """
        self._get_edges()
        self._get_edge_weights()
        self._generate_task(num_timesteps_in, num_timesteps_out)
        dataset = StaticGraphDiscreteSignal(self.edges, self.edge_weights, self.features, self.targets)

        return dataset
