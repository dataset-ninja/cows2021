Dataset **Cows2021** can be downloaded in [Supervisely format](https://developer.supervisely.com/api-references/supervisely-annotation-json-format):

 [Download](https://assets.supervisely.com/supervisely-supervisely-assets-public/teams_storage/1/v/ag/OiVbDpq2H3JrxpdulAmPgaWun1bBPXJuW09d8UrnhjxF5vYe611Q8yQmYqKjZR476laP5lrIVL8WgCQ60eVCfjicEQyYYMFj0QQhaoeS5FFnfxTQv4kGyIwZBh2Q.tar)

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