Dataset **Cows2021** can be downloaded in [Supervisely format](https://developer.supervisely.com/api-references/supervisely-annotation-json-format):

 [Download](https://assets.supervisely.com/supervisely-supervisely-assets-public/teams_storage/C/Q/mJ/j65Hp6pfhgM96IuIkxp0fWQqxDdmme9n97r6N5wbf9yp3GOOJTKaAd8bspOvQde2W52oaT8QBrJug0AvWbN5LjAXFhse3b9QniIQC3iXE5Mo5K2gRmewrHmaPCcD.tar)

As an alternative, it can be downloaded with *dataset-tools* package:
``` bash
pip install --upgrade dataset-tools
```

... using following python code:
``` python
import dataset_tools as dtools

dtools.download(dataset='Cows2021', dst_dir='~/dataset-ninja/')
```
Make sure not to overlook the [python code example](https://developer.supervisely.com/getting-started/python-sdk-tutorials/iterate-over-a-local-project) available on the Supervisely Developer Portal. It will give you a clear idea of how to effortlessly work with the downloaded dataset.

The data in original format can be [downloaded here](https://data.bris.ac.uk/datasets/tar/4vnrca7qw1642qlwxjadp87h7.zip).